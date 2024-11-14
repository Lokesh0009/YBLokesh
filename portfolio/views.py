from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.timezone import now
from .models import BlogPost, Comment, VisitorProfile
from portfolio.models import BlogPost, Comment, VisitorProfile
from .forms import BlogPostForm, CommentForm
import json
import requests
import csv
from django.http import Http404

API_TOKEN = 'dd69563fa6b218'  

def welcomePage_view(request):
    return render(request, "welcomePage.html")

def blog_list(request):
    all_posts = BlogPost.all()
    posts = sorted(all_posts, key=lambda x: x.published_date, reverse=True)
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog_list.html', {
        'page_obj': page_obj
    })

def blog_detail(request, id):
    post = next((p for p in BlogPost.all() if p.id == id), None)
    if not post:
        raise Http404("Blog post not found")
    
    comments = [comment for comment in Comment.all() if comment.blog_post_title == post.title]

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog_detail', id=post.id)
    else:
        form = CommentForm(initial={'blog_post_title': post.title})

    return render(request, 'blog_detail.html', {
        'post': post,
        'comments': comments,
        'form': form
    })

def blog_create(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = BlogPost(
                title=form.cleaned_data['title'],
                content=form.cleaned_data['content'],
                author=form.cleaned_data['author'],
            )
            if form.cleaned_data['image']:
                new_post.image = form.cleaned_data['image']
            if form.cleaned_data['pdf']:
                new_post.pdf = form.cleaned_data['pdf']

            new_post.save() 
            return redirect('blog_list')
    else:
        form = BlogPostForm()
    
    return render(request, 'blog_create.html', {'form': form})

@login_required
def delete_post(request, post_id):
    posts = BlogPost.all()
    post_to_delete = next((p for p in posts if p.id == post_id), None)

    if not post_to_delete:
        return render(request, '404.html', status=404)
    if request.user.is_staff or request.user.is_superuser:
        posts.remove(post_to_delete)
        with open('data/posts.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(BlogPost.fields)
            for post in posts:
                writer.writerow([
                    post.id, post.title, post.content, post.image, post.pdf,
                    post.published_date, post.author
                ])
                
        return redirect('blog_list')
    else:
        return HttpResponseForbidden("You are not authorized to delete this post.")


# @permission_required('yourappname.can_delete_post', raise_exception=True)
# def delete_post(request, post_id):
#     posts = Post.all()
#     post_to_delete = next((p for p in posts if p.title == post_id), None)
#     if not post_to_delete:
#         return render(request, '404.html', status=404)
    
#     posts.remove(post_to_delete)
    
#     with open('data/posts.csv', 'w', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow(["title", "content"])  # headers
#         for post in posts:
#             writer.writerow([post.title, post.content])
    
#     return redirect('post_list')


import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def track_analytics(request):
    if request.method == 'POST':
        try:
            # Check for empty body
            if not request.body:
                return JsonResponse({'error': 'Empty request body'}, status=400)
            
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        # Extract data from the POST request
        page_urls = data.get("page_urls", [])
        scroll_depth = data.get("scroll_depth", [])
        time_spent = data.get("time_spent", [])
        country = data.get("country", "Unknown")
        region = data.get("region", "Unknown")
        utm_source = data.get("utm_source")

        print("Received data:", data)

        # Retrieve the session ID
        session_id = request.session.session_key
        visitor_profiles = VisitorProfile.all()  # Load all profiles from CSV
        visitor_profile = next((vp for vp in visitor_profiles if vp.session_id == session_id), None)

        if visitor_profile:
            # Update the existing profile with new data
            visitor_profile.page_urls.extend(page_urls)
            visitor_profile.scroll_depth.extend(scroll_depth)
            visitor_profile.time_spent.extend(time_spent)
            visitor_profile.utm_source = utm_source or visitor_profile.utm_source
            
            # Update country and region if they are unknown
            if visitor_profile.country == 'Unknown' or visitor_profile.region == 'Unknown':
                if country == 'Unknown' and region == 'Unknown':
                    country, region = get_country_and_region(get_client_ip(request))
                
                visitor_profile.country = country
                visitor_profile.region = region

            # Save updated profile back to CSV
            visitor_profile.update()

            return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'failure'}, status=400)



# Helper Functions

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_country_and_region(ip_address):
    response = requests.get(f'https://ipinfo.io/{ip_address}/json?token={API_TOKEN}')
    
    if response.status_code == 200:
        data = response.json()
        country = data.get('country', 'Unknown')
        region = data.get('region', 'Unknown')
        return country, region
    else:
        print("Failed to fetch data:", response.status_code)
        return 'Unknown', 'Unknown'
