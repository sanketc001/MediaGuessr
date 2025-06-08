from mcp.server.fastmcp import FastMCP
import os.path
import requests
from imdb import Cinemagoer
from youtube_search import YoutubeSearch
import shutil

IMDB = Cinemagoer()

mcp = FastMCP("MediaGuessr", instructions="MediaGuessr Assistant")

@mcp.tool()
def get_info_imdb_id(imdb_id: str) -> dict:
    """Fetch movie or show information from IMDb using its IMDB ID.

    Args:
        imdb_id (str): The name of the movie to look up. e.g: "1234567"

    Returns:
        dict: A dictionary containing movie information. 
    """
    try:
        # Search for the movie
        movies = IMDB.get_movie(imdb_id)
        if not movies:
            return {"error": "Movie not found"}
        
        data={}
        # Return the movie information as a dictionary
        for key, value in movies.items():
            # print(key, value)
            if isinstance(value, list):
                data[key] = [str(item) for item in value]
            elif isinstance(value, dict):
                data[key] = {k: str(v) for k, v in value.items()}
            else:
                data[key] = str(value)
        return data
    except Exception as e:
        return {"error": str(e)}

# print(get_info_imdb_id("0111161"))


@mcp.tool()
def get_user_location():
    """
    Detect approximate location (latitude, longitude, city, country) based on public IP.

    Returns:
        dict: Contains latitude, longitude, city, region, country.
    """
    try:
        response = requests.get("http://ip-api.com/json/")
        data = response.json()

        if data.get("status") != "success":
            return {"error": "Could not determine location."}

        location = {
            "latitude": data.get("lat"),
            "longitude": data.get("lon"),
            "city": data.get("city"),
            "region": data.get("regionName"),
            "country": data.get("country"),
            "ip": data.get("query")
        }

        return location
    except Exception as e:
        return {"error": str(e)}
    

# function to copy file to current directory
# @mcp.tool()
# def copy_file(file_path: str) -> str:
#     """
#     Copy a file to the current directory.

#     Args:
#         file_path (str): The path of the file to copy.

#     Returns:
#         str: The path of the copied file.
#     """
#     try:
#         # Get the current directory
#         current_directory = os.getcwd()
        
#         # Copy the file to the current directory
#         shutil.copy(file_path, current_directory)
        
#         return os.path.join(current_directory, os.path.basename(file_path))
#     except Exception as e:
#         return {"error": str(e)}
    

@mcp.tool()
def youtube_recipe_search(query: str) -> dict:
    """Search for YouTube videos for a dish/food recipe.
    
    Args:
        query (str): Search query for YouTube.
    
    Returns:
        dict: Video Search results.
    """
    try:
        # Perform the search
        results = YoutubeSearch(query, max_results=2).to_dict()

        return results
    except Exception as e:
        return {
            "success": False,
            "message": f"Error searching YouTube: {str(e)}"
        }




@mcp.prompt()
def hotel_search_assistant(location: str) -> str:
    """
    Create a hotel search assistant prompt for a specific location
    
    Args:
        location: The destination city or region to search for hotels
    """
    return f"""You are a helpful travel assistant specializing in hotel recommendations. I'm looking for hotels in {location}.

Please help me search for suitable accommodations by:

1. Using the search_hotels tool to find available options in {location}
2. Asking me about my preferences regarding:
   - Specific check-in and check-out dates
   - Number of guests
   - Budget range
   - Hotel amenities that are important to me (pool, gym, breakfast, etc.)
   - Preferred location within {location} (downtown, near airport, etc.)

Based on my responses, refine the search and provide recommendations. If I have specific dates or requirements, use them with the search_hotels tool to get more relevant results.

If I'm just browsing without firm dates, suggest popular hotels in {location} and provide general information about the best areas to stay, seasonal considerations, and any local events that might affect hotel availability or prices."""


@mcp.prompt()
def mediaGuessr()-> str:
    """Guess the media based on a description."""
    return """Agent: Media & Travel Assistant - Instruction Set
📥 Input:

    Image from a movie, show, game, or food scene.

🧠 Agent Tasks (Step by Step Logic):

    

    Detect Media Type:

        Classify the image:

            🎥 Scene from Movie/Show/Game.

            🍽️ Food/Dish image.

    For Movie/Show/Game Scene Images:
    🎞️ Identify the Source:

        Detect the name of the movie/show/game.
        If Imdb id exists.
        Get Imdb Info using get_info_imdb_id function.
        Mention where I can watch the movie/show , if game then mention the platform to play it.
    🎬 Scene Recognition:

        Identify the specific scene or location depicted (using landmarks, styles, metadata if available).
    📍 Location Breakdown:

        Find the real-world shooting location (city, country, landmark).

        Find the in-movie fictional location (if applicable).
    🌍 Trip Planning:

        Build a trip itinerary for the real-world location:

            Suggest nearby famous filming locations from other movies/games/shows.

            Include local experiences connected to the media theme.

            Suggest movie-themed cafes, restaurants, or tours in the area.
    🎮 Optional:

        If the image is from a game, suggest real-world equivalents (inspired by the game setting).

    For Food/Dish Images:
    🎞️ Identify Dish & Media:

        Recognize the dish.

        Identify the movie/show it's featured in (if applicable).
    🍽️ Recipe & Restaurant Discovery:

        Find popular YouTube or web recipes for the dish.

        Search for restaurants near the user (or globally known) that serve the dish.

    Output Structured Response:

        For Movie/Scene Image:

            Movie/Show/Game Name.

            Scene/Location details.

            Real-world shooting location.

            Fictional in-movie location (optional).

            Suggested travel plan with nearby media-related locations and themed activities.

        For Food Image:

            Dish Name.

            Movie/Show where it's featured.

            Recipe links (YouTube/Web) use MCP Tool Youtube Search with appropriate query.

            Restaurant suggestions (based on user location or famous spots).

⚙️ Notes:

    Always cross-reference results from multiple sources (IMDB, Google Images, Reverse Image Search, YouTube, Maps APIs).

    Prefer accuracy over speed.

    If multiple guesses possible, show top 3 probable matches.

    When planning trips, add pop culture trivia for user engagement."""


