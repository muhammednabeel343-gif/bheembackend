from datetime import date
from sqlalchemy.orm import Session
from app.models.game import Game
from app.models.requirement import Requirement


def seed_sample_games(db: Session) -> None:
    if db.query(Game).count() > 0:
        return

    games = [
        # Cyberpunk 2077
    {
"name": "Cyberpunk 2077",
        "genre": "Action RPG",
        "category": "Open World",
        "publisher": "CD Projekt Red",
        "release_date": date(2020, 12, 10),
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1091500/library_600x900.jpg",
        "requirements": {
            "cpu": "Intel Core i5-3570K",
            "gpu": "GTX 970",
            "ram": 8,
            "storage": 70,
        "directx": "12",
        "operating_system": "Windows 10",
    },
},

    # Red Dead Redemption 2
    {
        "name": "Red Dead Redemption 2",
        "slug": "red-dead-redemption-2",
        "genre": "Action Adventure",
        "category": "Open World",
        "publisher": "Rockstar Games",
        "release_date": date(2018, 10, 26),
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1174180/library_600x900.jpg",
        "requirements": {
            "cpu": "Intel Core i5-2500K",
            "gpu": "GTX 770",
            "ram": 8,
            "storage": 150,
            "directx": "12",
            "operating_system": "Windows 10",
        },
    },

    # Elden Ring
    {
        "name": "Elden Ring",
        "slug": "elden-ring",
        "genre": "Action RPG",
        "category": "Soulslike",
        "publisher": "FromSoftware",
        "release_date": date(2022, 2, 25),
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1245620/library_600x900.jpg",
        "requirements": {
            "cpu": "Intel Core i5-8400",
            "gpu": "GTX 1060 3GB",
            "ram": 12,
            "storage": 60,
            "directx": "12",
            "operating_system": "Windows 10",
        },
    },

    # Forza Horizon 5
    {
        "name": "Forza Horizon 5",
        "slug": "forza-horizon-5",
        "genre": "Racing",
        "category": "Open World Racing",
        "publisher": "Xbox Game Studios",
        "release_date": date(2021, 11, 9),
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1551360/library_600x900.jpg",
        "requirements": {
            "cpu": "Intel Core i5-4460",
            "gpu": "GTX 970",
            "ram": 8,
            "storage": 110,
            "directx": "12",
            "operating_system": "Windows 10",
        },
    },

    # Black Myth Wukong
    {
        "name": "Black Myth: Wukong",
        "slug": "black-myth-wukong",
        "genre": "Action RPG",
        "category": "Action",
        "publisher": "Game Science",
        "release_date": date(2024, 8, 20),
        "description": "Journey through Chinese mythology.",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/2358720/library_600x900.jpg",
        "cover_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/2358720/library_600x900.jpg",
        "official_link": "https://www.heishenhua.com",
        "requirements": {
            "cpu": "Intel Core i7-9700K",
            "gpu": "RTX 3070",
            "ram": 16,
            "storage": 130,
            "directx": "12",
            "operating_system": "Windows 10",
        },
    },

    # The Last of Us Part I
    {
        "name": "The Last of Us Part I",
        "slug": "the-last-of-us-part-i",
        "genre": "Action Adventure",
        "category": "Story",
        "publisher": "Naughty Dog",
        "release_date": date(2023, 3, 28),
        "description": "Experience the emotional story of Joel and Ellie.",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1888930/library_600x900.jpg",
        "cover_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1888930/library_600x900.jpg",
        "official_link": "https://www.playstation.com",
        "requirements": {
            "cpu": "Intel Core i7-9700K",
            "gpu": "RTX 2070 Super",
            "ram": 16,
            "storage": 100,
            "directx": "12",
            "operating_system": "Windows 10",
        },
    },

    # Star Citizen
    
    ]

    for game_data in games:
        game = Game(
            name=game_data["name"],
            genre=game_data["genre"],
            category=game_data["category"],
            publisher=game_data["publisher"],
            release_date=game_data["release_date"],
            image_url=game_data["image_url"],
        )
        db.add(game)
        db.flush()
        requirement_data = game_data["requirements"]
        requirement = Requirement(
            game_id=game.id,
            cpu=requirement_data["cpu"],
            gpu=requirement_data["gpu"],
            ram=requirement_data["ram"],
            storage=requirement_data["storage"],
            directx=requirement_data.get("directx"),
            operating_system=requirement_data.get("operating_system"),
        )
        db.add(requirement)

    db.commit()
