from datetime import date
from sqlalchemy.orm import Session
from app.models.game import Game
from app.models.requirement import Requirement

def seed_sample_games(db: Session) -> None:
    if db.query(Game).count() > 0:
        return

    games = [
        {
            "name": "Cyberpunk 2077",
            "genre": "Action RPG",
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
        {
            "name": "Red Dead Redemption 2",
            "genre": "Action Adventure",
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
        {
            "name": "Elden Ring",
            "genre": "Action RPG",
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
        {
            "name": "Forza Horizon 5",
            "genre": "Racing",
            "publisher": "Xbox Game Studios",
            "release_date": date(2021, 11, 9),
            "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1551360/library_600x900.jpg",
            "description": "Experience an open-world racing adventure across Mexico with stunning visuals and dynamic seasons.",
            "price": 1499.0,
            "requirements": {
                "cpu": "Intel Core i5-4460",
                "gpu": "GTX 970",
                "ram": 8,
                "storage": 110,
                "directx": "12",
                "operating_system": "Windows 10",
            },
        },
        {
            "name": "A Plague Tale: Requiem",
            "genre": "Action Adventure",
            "publisher": "Focus Entertainment",
            "release_date": date(2022, 10, 18),
            "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1805630/library_600x900.jpg",
            "description": "A Plague Tale: Requiem continues the journey of Amicia and Hugo in a beautifully haunting adventure.",
            "price": 499.0,
            "requirements": {
                "cpu": "Intel Core i5-4690K",
                "gpu": "NVIDIA GeForce GTX 970",
                "ram": 8,
                "storage": 50,
                "directx": "11",
                "operating_system": "Windows 10",
            },
        },
    ]

    for game_data in games:
        game = Game(
            name=game_data["name"],
            genre=game_data["genre"],
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