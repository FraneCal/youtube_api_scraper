import pandas as pd
from googleapiclient.discovery import build

api_key = 'YOUR_API_KEY_HERE'  # Replace with your API key

youtube = build('youtube', 'v3', developerKey=api_key)

# Retrieve the channel ID for the given username
channel_request = youtube.channels().list(
    part='snippet,contentDetails',
    forUsername='BBCNews'
)
channel_response = channel_request.execute()

# Extract channel username and ID
channel_username = channel_response['items'][0]['snippet']['title']
channel_id = channel_response['items'][0]['id']

# Initialize variables for pagination
next_page_token = None
all_videos = []

# Retrieve all videos from the channel
while True:
    videos_request = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        type='video',
        order='date',
        maxResults=50,  # Maximum results per page
        pageToken=next_page_token
    )
    videos_response = videos_request.execute()
    
    all_videos.extend(videos_response['items'])

    next_page_token = videos_response.get('nextPageToken')
    if not next_page_token:
        break  # Break the loop if there are no more pages

# Initialize lists to store extracted information
titles = []
published_dates = []
likes = []
views = []
descriptions = []
urls = []

# Extract information from each video
for video in all_videos:
    video_id = video['id']['videoId']
    video_title = video['snippet']['title']
    video_description = video['snippet']['description']
    video_published_at = video['snippet']['publishedAt']
    video_url = f'https://www.youtube.com/watch?v={video_id}'

    # Retrieve statistics for each video
    video_statistics_request = youtube.videos().list(
        part='statistics',
        id=video_id
    )
    video_statistics_response = video_statistics_request.execute()
    video_statistics = video_statistics_response['items'][0]['statistics']
    video_likes = int(video_statistics.get('likeCount', 0))
    video_views = int(video_statistics.get('viewCount', 0))

    # Append extracted information to lists
    titles.append(video_title)
    published_dates.append(video_published_at)
    likes.append(video_likes)
    views.append(video_views)
    descriptions.append(video_description)
    urls.append(video_url)

# Create a DataFrame from the lists
data = {
    'Title': titles,
    'Published Date': published_dates,
    'Likes': likes,
    'Views': views,
    'Description': descriptions,
    'URL': urls
}
df = pd.DataFrame(data)

# Save DataFrame to Excel file with channel username as filename
excel_file_path = f'{channel_username}_videos.xlsx' 
df.to_excel(excel_file_path, index=False)

print("Excel file saved successfully.")
