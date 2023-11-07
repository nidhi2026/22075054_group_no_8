from django.shortcuts import render, redirect
import kitsu
from .models import *
from .forms import *
from asgiref.sync import sync_to_async
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import timezone
import asyncio
from django.contrib.auth.decorators import login_required

genres_list = [ "Action","Adventure","Comedy","Fantasy","Horror","Mecha","Music","Mystery","Psychological","Romance","Sci-Fi","Slice of Life","Sports","Supernatural","Thriller"]

# Create your views here.
async def trending(request):
    client = kitsu.Client()
    tre_animes = await client.trending_anime()

    genres_list = [ "Action","Adventure","Comedy","Fantasy","Horror","Mecha","Music","Mystery","Psychological","Romance","Sci-Fi","Slice of Life","Sports","Supernatural","Thriller"]

    response = await sync_to_async(render)(request, 'index.html', {'animes': tre_animes, 'genres_list':genres_list})
    return response


async def get_anime(request, anime_id):
    client = kitsu.Client()
    anime = await client.get_anime(anime_id)

    # Fetch genres and await the coroutine
    genres = [genre.title for genre in await anime.categories]
    streaming_links = [{'title':streams.title,'url':streams.url} for streams in await anime.streaming_links]

    user = request.user

    # Check if the anime is in the watchlist
    watchlist_item = await sync_to_async(WatchList.objects.filter)(user=user, anime_id=anime_id)
    unwatched = await sync_to_async(watchlist_item.exists)()

    # Check if anime is liked by user
    reaction_item = await sync_to_async(Reaction_anime.objects.filter)(user=user, anime_id=anime_id, reaction_type=Reaction_anime.LIKE)
    liked = await sync_to_async(reaction_item.exists)()

    # Check of anime is disliked by user
    reaction_item_d = await sync_to_async(Reaction_anime.objects.filter)(user=user, anime_id=anime_id, reaction_type=Reaction_anime.DISLIKE)
    disliked = await sync_to_async(reaction_item_d.exists)()

    comments = await sync_to_async(Comment_anime.objects.filter)(anime_id=anime_id)
    comment_form = CommentFormAnime()
    if request.method == 'POST':
        post_type = request.POST.get('post_type')
        
        if post_type == 'comment':
            comment_form = CommentFormAnime(data=request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.anime_id = anime_id
                await sync_to_async(setattr)(new_comment, 'user', request.user)
                new_comment.created_at = (await sync_to_async(timezone.now)()).date()
                await sync_to_async(new_comment.save)()
                return HttpResponseRedirect(request.path_info)
        elif post_type == 'reaction':
            reaction_type = request.POST.get('reaction_type')
            anime_id = request.POST.get('anime_id')  # Use get() to avoid KeyError
            user = request.user
            print('reaction',reaction_type, 'anime:',anime_id)
            reaction_item = await sync_to_async(Reaction_anime.objects.filter)(user=user, anime_id=anime_id)
            if reaction_type == 'like':
                first_item = await sync_to_async(reaction_item.first)()
                if await sync_to_async(reaction_item.exists)() and first_item.reaction_type == Reaction_anime.LIKE:  # If this anime is already liked
                    await sync_to_async(reaction_item.delete)()  # Remove the like
                    liked = False  # Set its liked status to False
                else: 
                    reaction, created = await sync_to_async(Reaction_anime.objects.get_or_create)(user=user, anime_id=anime_id)  # Add it to reactions or get it if it already exists
                    reaction.reaction_type = Reaction_anime.LIKE
                    await sync_to_async(reaction.save)()
                    liked = True  # Set its liked status to True only if it was created
            elif reaction_type == 'dislike':
                first_item = await sync_to_async(reaction_item_d.first)()
                if await sync_to_async(reaction_item_d.exists)() and first_item.reaction_type == Reaction_anime.DISLIKE:  # If this anime is already disliked
                    await sync_to_async(reaction_item_d.delete)()  # Remove the like
                    disliked = False  # Set its liked status to False
                else: 
                    reaction, created = await sync_to_async(Reaction_anime.objects.get_or_create)(user=user, anime_id=anime_id)  # Add it to reactions or get it if it already exists
                    reaction.reaction_type = Reaction_anime.DISLIKE
                    await sync_to_async(reaction.save)()
                    disliked = True  # Set its liked status to True only if it was created
            return HttpResponseRedirect(request.path_info)


        elif post_type == 'watchlater':
            anime_id = request.POST.get('anime_id')  # Use get() to avoid KeyError
            user = request.user

            watchlist_item = await sync_to_async(WatchList.objects.filter)(user=user, anime_id=anime_id)
            if await sync_to_async(watchlist_item.exists)():  # If this anime is already marked as unwatch
                await sync_to_async(watchlist_item.delete)()  # Remove it from watchlist
                unwatched = False  # Set its unwatch status to False
            else: 
                watchlist_item, created = await sync_to_async(WatchList.objects.get_or_create)(user=user, anime_id=anime_id)  # Add it to watchlist or get it if it already exists
                unwatched = True  # Set its unwatch status to True only if it was created
            return HttpResponseRedirect(request.path_info)
    else:
        comment_form = CommentFormAnime()

    likes = await sync_to_async(Reaction_anime.objects.filter(anime_id=anime_id, reaction_type=Reaction_anime.LIKE).count)()
    dislikes = await sync_to_async(Reaction_anime.objects.filter(anime_id=anime_id, reaction_type=Reaction_anime.DISLIKE).count)()
    anime_names = (anime.abbreviated_titles)[:3]
    response = await sync_to_async(render)(request, 'anime/anime_details.html', {
                                                        'anime': anime, 'genres': genres, 
                                                        'streaming_links':streaming_links,
                                                        'unwatch': unwatched,
                                                        'liked':liked,
                                                        'disliked':disliked,
                                                        'comment_form': comment_form,
                                                        'comments':comments,
                                                        'likes':likes,
                                                        'dislikes':dislikes,
                                                        'names':anime_names,
                                                        'you':user,
                                                        'genres_list':genres_list,
                                                        })
    return response


async def get_manga(request, manga_id):
    client = kitsu.Client()
    manga = await client.get_manga(manga_id)

    # Fetch genres and await the coroutine
    genres = [genre.title for genre in await manga.categories]

    user = request.user

    # Check if the anime is in the watchlist
    readlist_item = await sync_to_async(ReadList.objects.filter)(user=user, manga_id=manga_id)
    unread = await sync_to_async(readlist_item.exists)()

    # Check if manga is liked by user
    reaction_item = await sync_to_async(Reaction_manga.objects.filter)(user=user, manga_id=manga_id, reaction_type=Reaction_manga.LIKE)
    liked = await sync_to_async(reaction_item.exists)()

    # Check of manga is disliked by user
    reaction_item_d = await sync_to_async(Reaction_manga.objects.filter)(user=user, manga_id=manga_id, reaction_type=Reaction_manga.DISLIKE)
    disliked = await sync_to_async(reaction_item_d.exists)()

    comments = await sync_to_async(Comment_manga.objects.filter)(manga_id=manga_id)
    comment_form = CommentFormManga()
    if request.method == 'POST':
        post_type = request.POST.get('post_type')
        
        if post_type == 'comment':
            comment_form = CommentFormManga(data=request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.manga_id = manga_id
                await sync_to_async(setattr)(new_comment, 'user', request.user)
                new_comment.created_at = (await sync_to_async(timezone.now)()).date()
                await sync_to_async(new_comment.save)()
                return HttpResponseRedirect(request.path_info)
        
        elif post_type == 'reaction':
            reaction_type = request.POST.get('reaction_type')
            manga_id = request.POST.get('manga_id')  # Use get() to avoid KeyError
            user = request.user
            
            reaction_item = await sync_to_async(Reaction_manga.objects.filter)(user=user, manga_id=manga_id)
            if reaction_type == 'like':
                first_item = await sync_to_async(reaction_item.first)()
                if await sync_to_async(reaction_item.exists)() and first_item.reaction_type == Reaction_manga.LIKE:  # If this anime is already liked
                    await sync_to_async(reaction_item.delete)()  # Remove the like
                    liked = False  # Set its liked status to False
                else: 
                    reaction, created = await sync_to_async(Reaction_manga.objects.get_or_create)(user=user, manga_id=manga_id)  # Add it to reactions or get it if it already exists
                    reaction.reaction_type = Reaction_manga.LIKE
                    await sync_to_async(reaction.save)()
                    liked = True  # Set its liked status to True only if it was created
            elif reaction_type == 'dislike':
                first_item = await sync_to_async(reaction_item_d.first)()
                if await sync_to_async(reaction_item_d.exists)() and first_item.reaction_type == Reaction_manga.DISLIKE:  # If this anime is already disliked
                    await sync_to_async(reaction_item_d.delete)()  # Remove the like
                    disliked = False  # Set its liked status to False
                else: 
                    reaction, created = await sync_to_async(Reaction_manga.objects.get_or_create)(user=user, manga_id=manga_id)  # Add it to reactions or get it if it already exists
                    reaction.reaction_type = Reaction_manga.DISLIKE
                    await sync_to_async(reaction.save)()
                    disliked = True  # Set its liked status to True only if it was created
            return HttpResponseRedirect(request.path_info)

        elif post_type == 'readlater':
            manga_id = request.POST.get('manga_id')  # Use get() to avoid KeyError
            user = request.user

            readlist_item = await sync_to_async(ReadList.objects.filter)(user=user, manga_id=manga_id)
            if await sync_to_async(readlist_item.exists)():  # If this anime is already marked as unwatch
                await sync_to_async(readlist_item.delete)()  # Remove it from watchlist
                unread = False  # Set its unwatch status to False
            else: 
                readlist_item, created = await sync_to_async(ReadList.objects.get_or_create)(user=user, manga_id=manga_id)  # Add it to watchlist or get it if it already exists
                unread = True  # Set its unwatch status to True only if it was created
            return HttpResponseRedirect(request.path_info)
    else:
        comment_form = CommentFormManga()

    likes = await sync_to_async(Reaction_manga.objects.filter(manga_id=manga_id, reaction_type=Reaction_manga.LIKE).count)()
    dislikes = await sync_to_async(Reaction_manga.objects.filter(manga_id=manga_id, reaction_type=Reaction_manga.DISLIKE).count)()

    response = await sync_to_async(render)(request, 'manga/manga_details.html', {
                                                        'manga': manga, 'genres': genres, 
                                                        'unread': unread,
                                                        'liked':liked,
                                                        'disliked':disliked,
                                                        'comment_form': comment_form,
                                                        'comments':comments,
                                                        'likes':likes,
                                                        'dislikes':dislikes,
                                                        'you':user,
                                                        'genres_list':genres_list,
                                                        })
    return response


async def get_genre_anime(request, genre):
    client = kitsu.Client()
    animes = await client.search_anime(genres=[genre.lower()], limit=15)
    genre_anime=[]
    for anime in animes:
        if anime.title!=None:
            ani=await client.get_anime(anime.id)
            genre_anime.append(ani)
    response = await sync_to_async(render)(request, 'anime/genre_anime.html', context={'genre_anime':genre_anime, 'genre':genre, 'genres_list':genres_list})
    return response

async def get_genre_manga(request, genre):
    client = kitsu.Client()
    mangas = await client.search_manga(genres=[genre.lower()], limit=15
                                       )
    genre_manga=[]
    for manga in mangas:
        if manga.title!=None:
            man=await client.get_manga(manga.id)
            genre_manga.append(man)
    response = await sync_to_async(render)(request, 'manga/genre_manga.html', context={'genre_manga':genre_manga, 'genre':genre, 'genres_list':genres_list})
    return response

async def watchlist(request):
    # Define a synchronous function to fetch data from the database
    def fetch_data():
        watchlater = WatchList.objects.filter(user=request.user)
        return [anime.anime_id for anime in watchlater]

    # Call the synchronous function using sync_to_async
    data = await sync_to_async(fetch_data)()
    watchlist = []

    client = kitsu.Client()
    for anime_id in data:
        a = await client.get_anime(anime_id)
        watchlist.append({'anime_id':anime_id, 'title':a.title, 'image':a.poster_image(_type='small')})
    watchlist=watchlist[::-1]

    render_func = sync_to_async(render, thread_sensitive=True)
    return await render_func(request, 'anime/watchlist.html', {'watchlater': watchlist, 'genres_list':genres_list})

async def readlist(request):
    # Define a synchronous function to fetch data from the database
    def fetch_data():
        readlater = ReadList.objects.filter(user=request.user)
        return [manga.manga_id for manga in readlater]

    # Call the synchronous function using sync_to_async
    data = await sync_to_async(fetch_data)()
    readlist = []

    client = kitsu.Client()
    for manga_id in data:
        a = await client.get_manga(manga_id)
        readlist.append({'manga_id':manga_id, 'title':a.title, 'image':a.poster_image})
    readlist=readlist[::-1]

    render_func = sync_to_async(render, thread_sensitive=True)
    return await render_func(request, 'manga/readlist.html', {'readlater': readlist, 'genres_list':genres_list})

async def search_kitsu(query):
    client = kitsu.Client()
    results = await client.search_anime(query, limit=15)
    # Convert Title objects to JSON-serializable format
    formatted_results = []
    for result in results:
        if result.title.en and query.lower() in (result.title.en).lower():
            formatted_results.append({
                'id':result.id,
                'title': result.title.en,
                'image_url': result.poster_image(_type='small')
            })
    if not formatted_results:
        return [{'title': "No anime available with this name", 'image_url': 'result.poster_image(_type="small")', 'genres_list':genres_list}]
    return formatted_results

def search(request):
    query = request.GET.get('q','abcdefghijklmnopqrstuvwxyz')
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(search_kitsu(query))
    # Check if the request is an AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Return a JSON response
        return JsonResponse(results, safe=False)
    # If it's not an AJAX request, render the template as usual
    return render(request, 'search.html', {'results': results, 'genres_list':genres_list})
