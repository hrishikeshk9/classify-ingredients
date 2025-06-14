from fastapi import FastAPI, Request, File, UploadFile, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from PIL import Image
import pytesseract
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import io

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.post("/ocr")
async def ocr(image: UploadFile = File(...)):
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File is not an image.")

    try:
        contents = await image.read()
        img = Image.open(io.BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file.")

    text = pytesseract.image_to_string(img)

    return JSONResponse(content={"text": text})

@app.get("/")
async def health():
    return JSONResponse(content={"health_status": "success"})


class TextInput(BaseModel):
    text: str

# Define keyword sets for classification
NON_VEG_KEYWORDS = {
    # Meat and poultry
    "chicken", "beef", "pork", "lamb", "mutton", "veal", "turkey", "duck", "goose",
    "rabbit", "venison", "bison", "elk", "pheasant", "quail", "ostrich", "alligator",
    "frog", "snail", "camel", "kangaroo", "boar",
    # Seafood
    "fish", "salmon", "tuna", "cod", "catfish", "trout", "bass", "halibut",
    "sardine", "anchovy", "mackerel", "herring", "snapper", "grouper", "flounder",
    "shellfish", "shrimp", "prawn", "crab", "lobster", "clam", "oyster", "mussel",
    "scallop", "octopus", "squid", "cuttlefish",
    # Eggs and egg products
    "egg", "egg yolk", "egg white", "mayonnaise", "albumin",
    # Animal-derived additives
    "gelatin", "isinglass", "carmine", "cochineal", "lard", "suet", "tallow",
    "dripping", "keratin", "pancreatin", "pepsin", "trypsin", "bone phosphate",
    "sodium caseinate", "whey protein", "casein", "butter", "ghee", "cream",
    "yogurt", "honey", "shellac", "castoreum", "lanolin", "collagen", "rennet",
    "chitosan", "chondroitin", "fish oil", "animal fat", "bone char",
    "animal protein hydrolysate", "animal-derived enzymes", "animal-derived lecithin",
    "animal-derived flavorings", "animal-derived emulsifiers", "animal-derived stabilizers",
    "animal-derived coloring agents", "animal-derived preservatives",
    "animal-derived waxes", "animal-derived gums", "animal-derived alcohols",
    "animal-derived acids", "animal-derived vitamins",
    # Processed meat products
    "bacon", "ham", "salami", "sausage", "pepperoni", "hot dog", "meatball",
    "jerky", "paté", "prosciutto", "chorizo",
    # Fish-based sauces and condiments
    "fish sauce", "anchovy paste", "oyster sauce", "shrimp paste",
    # Expand with many more animal species, processed meats, animal derivatives...
}

VEG_BUT_NOT_VEGAN_KEYWORDS = {
    # Dairy Products
    "milk", "whole milk", "skim milk", "low-fat milk", "condensed milk", "evaporated milk",
    "powdered milk", "buttermilk", "cream", "heavy cream", "light cream", "half and half",
    "sour cream", "clotted cream", "whipping cream", "double cream", "single cream",
    "yogurt", "greek yogurt", "plain yogurt", "flavored yogurt", "strained yogurt",
    "kefir", "cheese", "cheddar cheese", "mozzarella cheese", "parmesan cheese",
    "swiss cheese", "gouda cheese", "brie cheese", "camembert cheese", "blue cheese",
    "feta cheese", "ricotta cheese", "cream cheese", "cottage cheese", "paneer",
    "mascarpone", "quark", "halloumi", "colby cheese", "monterey jack", "provolone",
    "edam cheese", "emmental", "gruyere", "havarti", "limburger", "muenster cheese",
    "neufchatel cheese", "pecorino", "romano cheese", "stilton", "string cheese",
    "velveeta", "cheese curds", "cheese spread", "processed cheese", "cheese powder",
    "cheese sauce", "cheese dip", "cheese fondue", "cheese slices", "cheese sticks",
    "cheese balls", "cheese crisps", "cheese flakes", "cheese powder", "cheese flavoring",
    "cheese flavor", "cheese extract", "cheese powder", "cheese whey", "whey protein",
    "casein", "caseinate", "sodium caseinate", "calcium caseinate", "micellar casein",
    "milk protein concentrate", "milk protein isolate", "milk solids", "milk fat",
    "butter", "unsalted butter", "salted butter", "clarified butter", "ghee",
    "anhydrous milk fat", "butter oil", "butterfat", "butter milk solids",
    "butter powder", "butter flavor", "butter essence",
    
    # Eggs and Egg Products
    "egg", "eggs", "egg yolk", "egg white", "egg powder", "dried egg", "egg albumin",
    "egg protein", "egg lecithin", "egg substitute", "egg replacer", "egg wash",
    "mayonnaise", "aioli", "hollandaise sauce", "custard", "meringue", "quiche",
    "frittata", "omelette", "eggnog", "egg salad", "egg-based dressing", "egg-based sauce",
    "egg-based glaze", "egg-based binder", "egg-based emulsifier",
    
    # Honey and Bee Products
    "honey", "raw honey", "manuka honey", "clover honey", "wildflower honey",
    "acacia honey", "buckwheat honey", "orange blossom honey", "honeycomb",
    "bee pollen", "royal jelly", "propolis", "bee wax", "beeswax",
    
    # Dairy-Derived Additives and Ingredients
    "lactose", "milk sugar", "milk solids non-fat", "milk powder", "milk protein",
    "milk calcium", "milk phospholipids", "milk fat globule membrane",
    "milk concentrate", "milk derivative", "milk extract",
    
    # Animal-Derived Enzymes and Coagulants
    "rennet", "animal rennet", "microbial rennet", "vegetarian rennet", "chymosin",
    "pepsin", "lipase", "protease", "lactase", "galactase",
    
    # Other Dairy Products and Derivatives
    "ice cream", "gelato", "frozen yogurt", "custard", "buttermilk powder",
    "cream cheese", "sour cream powder", "cream powder", "yogurt powder",
    "cheese powder", "whey powder", "whey concentrate", "whey isolate",
    "milkshake", "milk-based beverage", "dairy beverage", "dairy dessert",
    
    # Butter and Fat Substitutes (Dairy-Based)
    "butter substitute", "butter flavor", "butter oil", "dairy fat", "milk fat",
    
    # Miscellaneous
    "caseinates", "dairy protein", "milk protein", "milk solids", "dairy solids",
    "milk derivative", "milk extract", "cream extract",
    
    # Processed Food Ingredients Containing Dairy or Eggs
    "custard powder", "egg powder", "egg protein concentrate", "milk protein concentrate",
    "dairy protein concentrate", "milk powder", "milk solids", "whey protein concentrate",
    "whey protein isolate", "casein hydrolysate", "lactalbumin", "lactoglobulin",
    
    # Common Dairy-Containing Food Items (vegetarian but not vegan)
    "cheesecake", "cream cheese frosting", "buttercream", "custard tart", "cream puff",
    "egg tart", "quiche lorraine", "frittata", "egg salad", "mayonnaise",
    
    # Dairy-Based Sauces and Dressings
    "ranch dressing", "caesar dressing", "blue cheese dressing", "alfredo sauce",
    "cheese sauce", "cream sauce", "béchamel sauce", "mornay sauce",
    
    # Dairy-Based Snacks and Desserts
    "yogurt parfait", "cheese dip", "cheese spread", "cheese ball", "cheese stick",
    "cheese cracker", "cream cheese dip", "sour cream dip", "butter cookie",
    "cheese cookie", "cheese biscuit", "cheese bread",
    
    # Dairy-Based Beverages
    "milkshake", "hot chocolate with milk", "latte", "cappuccino", "mocha", "chai latte",
    
    # Honey-Based Products
    "honey mustard", "honey glaze", "honey dressing", "honey butter",
    
    # Eggs in Processed Foods
    "egg noodle", "egg pasta", "egg bread", "egg roll", "egg wash",
    
    # Dairy and Egg Derivatives in Bakery
    "egg yolk powder", "egg white powder", "milk powder", "buttermilk powder",
    
    # Miscellaneous Animal-Derived Ingredients Allowed in Vegetarian Diets
    "lactose monohydrate", "milk protein hydrolysate", "milk calcium phosphate",
    "milk fat globule membrane", "milk phospholipids", "milk solids nonfat",
    
    # Add more common dairy and egg products to reach 1000+ entries by repeating variations,
    # regional names, processed forms, brand names, and scientific terms.
}

# TODO: [Future:Scope]
# To reach 1000+ keywords, you can programmatically expand this set by:
# 1. Adding regional/local names for dairy products.
# 2. Including scientific names and synonyms.
# 3. Adding brand names or common processed food items containing dairy/eggs/honey.
# 4. Including dairy-based additives and enzymes used in food processing.


@app.post("/categorize-food")
def categorize_food(input: TextInput):
    text_lower = input.text.lower()

    # Check non-veg keywords first
    if any(keyword in text_lower for keyword in NON_VEG_KEYWORDS):
        category = "non-veg"
    # Check vegetarian but not vegan keywords
    elif any(keyword in text_lower for keyword in VEG_BUT_NOT_VEGAN_KEYWORDS):
        category = "veg"
    else:
        category = "vegan"

    return {"category": category}





















    # data = {
    #     "veg": {
    #         "color": "#4CAF50",  # green
    #         "text": "VEG",
    #         "images": ["/static/veg1.png", "/static/veg2.png"],
    #     },
    #     "vegan": {
    #         "color": "#FFF9C4",  # light yellow
    #         "text": "VEGAN",
    #         "images": ["/static/vegan1.png", "/static/vegan2.png"],
    #     },
    #     "nonveg": {
    #         "color": "#FFCDD2",  # light red
    #         "text": "NON-VEG",
    #         "images": ["/static/nonveg1.png", "/static/nonveg2.png"],
    #     },
    # }
    # return templates.TemplateResponse(
    #     "category.html",
    #     {
    #         "request": request,
    #         "color": data[category]["color"],
    #         "text": data[category]["text"],
    #         "images": data[category]["images"],
    #     },
    # )

