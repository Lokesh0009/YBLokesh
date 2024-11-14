import csv
import os
from datetime import datetime
from django.conf import settings
from pytz import timezone
from django.core.files.storage import default_storage
import urllib.parse

NYC_TIMEZONE = timezone('America/New_York')

# Paths for CSV files
TAGS_CSV = os.path.join(settings.BASE_DIR, 'data', 'tags.csv')
BLOGPOSTS_CSV = os.path.join(settings.BASE_DIR, 'data', 'blogposts.csv')
COMMENTS_CSV = os.path.join(settings.BASE_DIR, 'data', 'comments.csv')
VISITORPROFILE_CSV = os.path.join(settings.BASE_DIR, 'data', 'visitorprofiles.csv')


def get_nyc_time():
    return datetime.now(NYC_TIMEZONE).isoformat()


# Helper function to ensure CSV file exists with headers
def ensure_csv_exists(file_path, headers):
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, mode='w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)

import uuid
class BlogPost:
    fields = ["id", "title", "content", "image", "pdf", "published_date", "author"]

    def __init__(self, title, content, image='', pdf='', author='', id=None, published_date=None):
        self.id = id or str(uuid.uuid4())  # Generate a unique ID if none is provided
        self.title = title
        self.content = content
        self.image = image  # Temporary storage for upload file object
        self.pdf = pdf  # Temporary storage for upload file object
        self.published_date = published_date or get_nyc_time()
        self.author = author

        # File paths for saved image and pdf
        self.image_path = image if isinstance(image, str) else ''
        self.pdf_path = pdf if isinstance(pdf, str) else ''

    def save(self):
        # Save image file
        if self.image and not isinstance(self.image, str):
            self.image_path = default_storage.save(f'blog_images/{self.image.name}', self.image)
        
        # Save PDF file
        if self.pdf and not isinstance(self.pdf, str):
            self.pdf_path = default_storage.save(f'blog_pdfs/{self.pdf.name}', self.pdf)

        # Save to CSV
        ensure_csv_exists(BLOGPOSTS_CSV, self.fields)
        with open(BLOGPOSTS_CSV, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                self.id, self.title, self.content, self.image_path, self.pdf_path,
                self.published_date, self.author
            ])

    @classmethod
    def all(cls):
        posts = []
        ensure_csv_exists(BLOGPOSTS_CSV, cls.fields)
        modified = False  
        with open(BLOGPOSTS_CSV, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row_id = row.get('id') or str(uuid.uuid4())
                if not row.get('id'):
                    row['id'] = row_id 
                    modified = True 

                post = cls(
                    title=row['title'],
                    content=row['content'],
                    image=row['image'],
                    pdf=row['pdf'],
                    author=row['author'],
                    id=row_id,
                    published_date=row['published_date']
                )
                posts.append(post)
        
        # Update CSV if any IDs were added
        if modified:
            with open(BLOGPOSTS_CSV, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=cls.fields)
                writer.writeheader()
                for post in posts:
                    writer.writerow({
                        'id': post.id,
                        'title': post.title,
                        'content': post.content,
                        'image': post.image_path,
                        'pdf': post.pdf_path,
                        'published_date': post.published_date,
                        'author': post.author,
                    })

        return posts

    def delete(self):
        posts = BlogPost.all()
        posts = [post for post in posts if post.id != self.id]
        ensure_csv_exists(BLOGPOSTS_CSV, self.fields)
        with open(BLOGPOSTS_CSV, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.fields)
            for post in posts:
                writer.writerow([
                    post.id, post.title, post.content, post.image_path, post.pdf_path,
                    post.published_date, post.author
                ])

    def update(self, **kwargs):
        posts = BlogPost.all()
        for post in posts:
            if post.id == self.id:
                for key, value in kwargs.items():
                    setattr(post, key, value)
        ensure_csv_exists(BLOGPOSTS_CSV, self.fields)
        with open(BLOGPOSTS_CSV, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.fields)
            for post in posts:
                writer.writerow([
                    post.id, post.title, post.content, post.image_path, post.pdf_path,
                    post.published_date, post.author
                ])

    def get_image_url(self):
        if self.image_path: 
            return f"{settings.MEDIA_URL}/blog_images/{self.image_path}" 
        return '/static/portfolio/images/unknown.png'
    
    def get_pdf_url(self):
        if self.pdf_path:
            encoded_path = urllib.parse.quote(self.pdf_path)
            return f"{settings.MEDIA_URL}blog_pdfs/{encoded_path}"
        return None

    def content_preview(self):
        return self.content[:100] + '...'

    def __str__(self):
        return self.title

# Comment model
class Comment:
    fields = ["blog_post_title", "author", "text", "created_at"]

    def __init__(self, blog_post_title, author, text):
        self.blog_post_title = blog_post_title
        self.author = author
        self.text = text
        self.created_at = get_nyc_time()

    def save(self):
        ensure_csv_exists(COMMENTS_CSV, self.fields)
        with open(COMMENTS_CSV, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([self.blog_post_title, self.author, self.text, self.created_at])

    @classmethod
    def all(cls, blog_post_title=None):
        """Retrieve all comments, or filter by blog post title if provided."""
        comments = []
        ensure_csv_exists(COMMENTS_CSV, cls.fields)
        with open(COMMENTS_CSV, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if blog_post_title is None or row['blog_post_title'] == blog_post_title:
                    comments.append(cls(row['blog_post_title'], row['author'], row['text']))
        return comments

    def __str__(self):
        return f'Comment by {self.author} on {self.blog_post_title}'

# VisitorProfile model
import csv
import os
import json
from datetime import datetime
from django.conf import settings
from pytz import timezone

NYC_TIMEZONE = timezone('America/New_York')
VISITORPROFILE_CSV = os.path.join(settings.BASE_DIR, 'data', 'visitorprofiles.csv')

def get_nyc_time():
    return datetime.now(NYC_TIMEZONE).isoformat()

def ensure_csv_exists(file_path, headers):
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, mode='w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)

class VisitorProfile:
    fields = [
        "session_id", "ip_address", "utm_source", "user_agent", "device_type",
        "page_urls", "scroll_depth", "time_spent", "country", "region", "date_time_visited"
    ]

    def __init__(self, session_id, ip_address, utm_source, user_agent, device_type,
                 page_urls, scroll_depth, time_spent, country="Unknown", region="Unknown"):
        self.session_id = session_id
        self.ip_address = ip_address
        self.utm_source = utm_source
        self.user_agent = user_agent
        self.device_type = device_type
        self.page_urls = page_urls
        self.scroll_depth = scroll_depth
        self.time_spent = time_spent
        self.country = country
        self.region = region
        self.date_time_visited = get_nyc_time()

    def save(self):
        ensure_csv_exists(VISITORPROFILE_CSV, self.fields)
        with open(VISITORPROFILE_CSV, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                self.session_id, self.ip_address, self.utm_source, self.user_agent, self.device_type,
                json.dumps(self.page_urls), json.dumps(self.scroll_depth), json.dumps(self.time_spent),
                self.country, self.region, self.date_time_visited
            ])

    @classmethod
    def all(cls):
        profiles = []
        ensure_csv_exists(VISITORPROFILE_CSV, cls.fields)
        with open(VISITORPROFILE_CSV, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                page_urls = json.loads(row["page_urls"])
                scroll_depth = json.loads(row["scroll_depth"])
                time_spent = json.loads(row["time_spent"])
                profiles.append(cls(
                    row["session_id"], row["ip_address"], row["utm_source"], row["user_agent"], row["device_type"],
                    page_urls, scroll_depth, time_spent, row["country"], row["region"]
                ))
        return profiles
    
    def update(self):
        profiles = VisitorProfile.all()
        
        # Find and update the existing profile
        for profile in profiles:
            if profile.session_id == self.session_id:
                profile.page_urls = self.page_urls
                profile.scroll_depth = self.scroll_depth
                profile.time_spent = self.time_spent
                profile.utm_source = self.utm_source
                profile.country = self.country
                profile.region = self.region
                profile.date_time_visited = self.date_time_visited

        # Rewrite the CSV with the updated profiles
        ensure_csv_exists(VISITORPROFILE_CSV, self.fields)
        with open(VISITORPROFILE_CSV, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.fields)
            for profile in profiles:
                writer.writerow([
                    profile.session_id, profile.ip_address, profile.utm_source, profile.user_agent,
                    profile.device_type, json.dumps(profile.page_urls), json.dumps(profile.scroll_depth),
                    json.dumps(profile.time_spent), profile.country, profile.region, profile.date_time_visited
                ])

    def delete(self):
        profiles = VisitorProfile.all()
        profiles = [profile for profile in profiles if profile.session_id != self.session_id]
        ensure_csv_exists(VISITORPROFILE_CSV, self.fields)
        with open(VISITORPROFILE_CSV, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.fields)
            for profile in profiles:
                writer.writerow([
                    profile.session_id, profile.ip_address, profile.utm_source, profile.user_agent,
                    profile.device_type, json.dumps(profile.page_urls), json.dumps(profile.scroll_depth),
                    json.dumps(profile.time_spent), profile.country, profile.region, profile.date_time_visited
                ])

    def __str__(self):
        return f'Session: {self.session_id}, Pages Visited: {self.page_urls}'
