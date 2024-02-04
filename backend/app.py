
import subprocess
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///scrapper.db"
db = SQLAlchemy(app)    #init database

class ProductResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    img = db.Column(db.String(1000))
    url = db.Column(db.String(1000))
    price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    search_text = db.Column(db.String(255))
    source = db.Column(db.String(255))

    def __ini__(self, name, img, url, price, search_text, source):
        self.name = name
        self.img = img
        self.url = url
        self.price = price
        self.search_text = search_text
        self.source = source

class TrackedProducts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tracked = db.Column(db.Boolean, default=True)

    def __init__(self, name, tracked=True):
        self.name = name
        self.tracked = tracked

# define router endpoints
@app.route("/results", methods=['POST'])
def submit_results():
    args = request.args.get("lang")
    #body = request.json.get("name")
    #return jsonify(f"lan {args} {body}")
    
    results = request.json.get('data')
    search_text = request.json.get("search_text")
    source = request.json.get("source")
    
    #return "strugling with dict iteration?", 200
    
    for result in results:
        product_result = ProductResult(
            name = results["name"],
            url = results["url"],
            img = results["img"],
            price = results["price"],
            search_text = search_text,
            source = source
        )
        db.session.add(product_result)
    
    db.session.commit()
    response = {"message": "Received data successfully"}
    return jsonify(response), 200

# Route for unique search texts  
@app.route("/unique_search_texts", methods=["GET"])
def get_unique_search_texts():
    unique_search_texts = db.session.query(
        ProductResult.search_text).distinct().all()
    unique_search_texts = [text[0] for text in unique_search_texts]
    return jsonify(unique_search_texts)

# Route for results
@app.route("/results")
def get_product_results():
    search_text = request.args.get("search_text")
    results = ProductResult.query.filter_by(search_text=search_text).order_by(
        ProductResult.created_at.desc()).all()
    
    product_dict = {}
    for result in results:
        url = result.url
        if url not in product_dict:
            product_dict[url] = {
                "name": result.name,
                "url": result.url,
                "img": result.img,
                "source": result.source,
                "created_at": result.created_at,
                "priceHistory": []
            }
    
    product_dict[url]["priceHistory"].append({
        "price": result.price,
        "date": result.created_at
    })

    formatted_results = list(product_dict.values())

    return jsonify(formatted_results)

# Route for 
@app.route("/all-results", methods=["GET"])
def get_results():
    results = ProductResult.query.all()
    product_results = []
    for result in results:
        product_results.append({
            "name": result.name,
            "url": result.url,
            "price": result.price,
            "img": result.img,
            "date": result.date,
            "created_at": result.created_at,
            "search_text": result.search_text,
            "source": result.source
        })
    
    return jsonify(product_results)


@app.route("/start-scraper", methods=["POST"])
def start_scrape():
    url = request.json.get('url')
    search_text = request.json.get("earch_text")

    # Run scrapper asynchronously in a seperate Pyhton process
    command = f"python .scrapper/__init__.py {url} \"{search_text}\" /results"
    subprocess.Popen(command, shell=True)

    response = {"message": "scrapper started successfully"}
    return jsonify(response),200

@app.route("/add-tracked-product", methods=["POST"])
def add_tracked_product():
    name = request.json.get("name")
    tracked_product = trackedproducts(name=name)
    db.session.add(tracked_product)
    db.session.commit()

    response = {"message": "Tracked product added successfully", "id": tracked_product.id}
    return jsonify(response), 200

@app.route("/tracked-product/<int:product_id>", methods=["PUT"])
def toggle_tracked_product(product_id):
    tracked_product = TrackedProducts.query.get(product_id)
    if (tracked_product is None):
        response = {'message': "Tracked product not found"}
        return jsonify(response), 404
    
    tracked_product.tracked = not tracked_product.tracked
    db.session.commit()

    response = {"message": "Tracked product toggled successfully"}
    return jsonify(response), 200

@app.route("/tracked-products", methods=["GET"])
def get_tracked_products():
    tracked_products = TrackedProducts.query.all()
    
    results = []
    for product in tracked_products:
        results.append({
            "id": product.id,
        })

    return jsonify(results), 200

@app.route("/update-tracked-products", methods=["POST"])
def update_tracked_products():
    tracked_products = TrackedProducts.query.all()
    url = "https://amazon.com"

    product_names = []
    for tracked_product in tracked_products:
        name = tracked_product.name
        if not tracked_product.tracked:
            continue

        command = f"python3 ./scrapper/__init__.py {url} \"{name}\" /results"
        subprocess.Popen(command, shell=True)
        product_names.append(name)

    response = {"message": "Scrapper started successfully", "products": product_names}
    return jsonify(response), 200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()





    