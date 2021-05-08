from flask import render_template, flash, redirect, url_for, request, session, g, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm, ProductForm, Profile, Explore
from app import app, db
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from bson import ObjectId
import json
from werkzeug.http import HTTP_STATUS_CODES
from datetime import datetime
from app.models import User
from datetime import datetime
import os


def error_response(status_code, message=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response

def bad_request(error_str):
    response = jsonify({"error":str(error_str)})
    response.status_code = 404
    return response

def ratingf(users):
    sums = int(users["rate"]["5"])+int(users["rate"]["4"])+int(users["rate"]["3"])+int(users["rate"]["2"])+int(users["rate"]["1"])
    if sums is not 0:
        rating = (5*int(users["rate"]["5"]) + 4*int(users["rate"]["4"]) + 3*int(users["rate"]["3"]) + 2*int(users["rate"]["2"]) + 1*int(users["rate"]["1"])) / (sums)
    else:
        rating = 0
    rating = round(rating, 2)
    return rating

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
# @login_required
def index():
    prod = db.products.find()
    form = Explore()
    if form.validate_on_submit():
        prodts = db.products.find( { '$text': { '$search': form.search.data } } )
        if prodts:
            flash(str(prodts.count())+" results for "+ form.search.data)
            return render_template('index.html', title='Search Products', prod=prodts, form=form)
        else:
            flash('No Products Found! :( ')
        return render_template('index.html', title='Search Products', form=form)
    return render_template('index.html', title='Home', prod=prod, form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        users = db.users
        login_u = users.find_one({'username':form.username.data})
        if login_u is None or not (check_password_hash(login_u['password_hash'],form.password.data)):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        session["username"] = form.username.data
        
        # g.username = form.username.data
        log_in_user = User(login_u)
        login_user(log_in_user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        else:
            return render_template('index.html', title='Sign In',form=form)
        return redirect(next_page)         
    return render_template('login.html', title='Sign In',form=form)

@app.route('/user/')
@login_required
def user():
    usern = session['username']
    users = db.users.find_one({"username":usern})
    rating = ratingf(users)
    prod = db.products.find({"user_name":usern})
    return render_template('user.html', users=users, prod=prod, rating=rating)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = Profile()
    usern = session['username']
    if form.prof_name.data:
        if form.validate_on_submit():
            users = db.users.find_one({"username":form.prof_name.data})
            prod = db.products.find({"user_name":form.prof_name.data})
            if users:
                rating = ratingf(users)
                return render_template('user.html', users=users, prod=prod, rating=rating)
            else:
                flash("No Seller Found by name")
                return render_template('profile.html', form=form, usern=usern)
        else:
            flash("No Seller Found by name")
    return render_template('profile.html', form=form, usern=usern)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        users = db.users
        existing_user = users.find_one({'username': form.username.data})

        if existing_user:
            flash('That username already exists..Try something else')
        else:
            password_hash = generate_password_hash(form.password.data)
            users.insert({'username': form.username.data,'email': form.email.data,'rate':{'1':'2','2':'1','3':'3','4':'9','5':'16'}, 'cart':[], 'password_hash': password_hash})
            flash('Registered!')
            return redirect(url_for('index'))
    
    return render_template('register.html',title = 'Register', form =form)

UPLOAD_PATH = "/Users/preyashgothane/Desktop/preyash/programs/python/flask/git_repo/SIH2020_marketplace/final_emark/app/"



@app.route('/product', methods=['GET', 'POST'])
def product():
    # form = ProductForm()
    form = ProductForm()
    if form.image.data:
        f = form.image.data
        filen = secure_filename(f.filename)
        image_data = form.image.name
        print(image_data)
        f.save(os.path.join(UPLOAD_PATH, 'static', filen))

    usern = session['username']
    if form.validate_on_submit():
        products = db.products
        products.insert({'prod_name': form.prod_name.data,'prod_value': form.prod_value.data, 'prod_desc': form.prod_desc.data, 'img':filen, 'user_name':usern })
        flash('Published!')
        return redirect(url_for('index'))
    return render_template('product.html', title='Enter Product',form=form, usern=usern)



@app.route('/explore', methods=['GET', 'POST'])
def explore():
    form = Explore()
    if form.validate_on_submit():
        prodts = db.products.find( { '$text': { '$search': form.search.data } } )
        if prodts:
            flash(str(prodts.count())+" results for "+ form.search.data)
            return render_template('explore.html', title='Search Products', prodts=prodts, form=form)
        else:
            flash('No Products Found! :( ')
        flash('No Products Found! :( ')
    return render_template('explore.html', title='Search Products', form=form)


@app.route('/addcart' , methods = ['GET', 'POST'])
@login_required
def addcart():
    if request.method == "POST":
        req = request.form
        id = req.get("pro_id")
        return redirect(url_for('adcart', pro_id = id))
    return render_template('base.html')

@app.route('/adcart' , methods = ['GET', 'POST'])
@login_required
def adcart():
    pro_id = request.args.get('pro_id', None)
    userc = session['username']
    db.users.update_one( { "username" : userc }, { '$addToSet' : { "cart":pro_id  } } )
    flash('Item Added to Cart')
    return redirect(url_for('index'))


@app.route('/remcart' , methods = ['GET', 'POST'])
@login_required
def remcart():
    if request.method == "POST":
        req = request.form
        id = req.get("pro_id")
        return redirect(url_for('removefcart', pro_id = id))
    return render_template('base.html')

@app.route('/removefcart', methods=['GET', 'POST'])
@login_required
def removefcart():
    userc = session['username']
    pro_id = request.args.get('pro_id', None)
    db.users.update_one( { "username" : userc }, { '$pull' : { "cart":pro_id } } )
    flash("Item Removed")
    return redirect(url_for('cart'))

@app.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    userc = session['username']
    cart = db.users.find_one({ "username":userc })
    id = cart["cart"]
    prodc=[]
    total = 0
    for k in id:
        d = db.products.find_one({ "_id" : ObjectId(k)  })
        prodc.append(d)
        total = total + int(d["prod_value"])
    return render_template('cart.html', title='Cart', prodc=prodc, userc=userc, total=total)







# db.users.updateOne( { "username" : "preyash" }, { $set : { "cart":["5ebf9f8d5eef0cbaa124c430", "5ec16de724c8c24b262102c0", "5ec13dbd85b2b082d53d865d"]  } } )

#---------------------------------------------------------------#

#APIs

#---------------------------------------------------------------#




#1 GET USER DETAILS / USER LOGIN API  
@app.route('/api/services/v1/getUserDetails', methods=['POST', 'GET'])
def get_user_details_api():
    response = jsonify({})
    response.status_code = 404
    try:
        data = json.loads(request.data)
        user = db.users.find_one({'username':data['Data']['username']})

        if ('username' not in data['Data'] or 'password' not in data['Data']):
            return bad_request('must include username and password fields')

        if user is None:
            return bad_request('Username does not exist')

        if check_password_hash(user['password_hash'],data['Data']['password']) == False:
            return bad_request('Password not matching')
        user_obj = {}
        user_obj["username"] = user["username"]
        user_obj["email"] = user["email"]
        user_obj["coordinates"] = user["coordinates"]
        user_obj["rate"] = user["rate"]
        user_obj["cart"] = user["cart"]
        response = jsonify({'ReturnMsg':'Success','user':user_obj})
        response.status_code = 200
    except Exception as e:
        print(e)
    return response

#2 PRODUCT SEARCH API 
@app.route('/api/services/v1/search',methods = ['POST'])
def search_api():
    response = jsonify({})
    response.status_code = 404
    try:
        data = json.loads(request.data)
        serial_no = data["Data"]["serial_no"]
        prod = db.products.find( { '$text': { '$search': serial_no } } )
        user_obj = {user_obj: {} for user_obj in range(prod.count())} #Creating Empty Nested Dic
        for k in range(0,prod.count()):   #Inserting Values into that Dic
            user_obj[k]["prod_name"] = prod[k]["prod_name"]
            user_obj[k]["prod_value"] = prod[k]["prod_value"]
            user_obj[k]["prod_desc"] = prod[k]["prod_desc"]
            user_obj[k]["img"] = prod[k]["img"]
            user_obj[k]["user_name"] = prod[k]["user_name"]
        response = jsonify({'ReturnMsg':'Success','user':user_obj}) 
        response.status_code = 200
    except Exception as e:
        print(e)
    return response

#3 GET ALL PRODUCTS FOR HOMEPAGE API
@app.route('/api/services/v1/getAllProducts', methods=['POST', 'GET'])
def get_all_products_api():
    response = jsonify({})
    response.status_code = 404
    try:
        data = json.loads(request.data)
        prod = db.products.find()
        user_obj = {user_obj: {} for user_obj in range(prod.count())} #Creating Empty Nested Dic
        for k in range(0,prod.count()):   #Inserting Values into that Dic
            user_obj[k]["prod_name"] = prod[k]["prod_name"]
            user_obj[k]["prod_value"] = prod[k]["prod_value"]
            user_obj[k]["prod_desc"] = prod[k]["prod_desc"]
            user_obj[k]["img"] = prod[k]["img"]
            user_obj[k]["user_name"] = prod[k]["user_name"]
        response = jsonify({'ReturnMsg':'Success','user':user_obj}) 
        response.status_code = 200
    except Exception as e:
        print(e)
    return response

#4 SHOW USER ADDED PRODUCTS IN CART API
@app.route('/api/services/v1/getUserCartProducts', methods=['POST', 'GET'])
def get_user_cart_api():
    response = jsonify({})
    response.status_code = 404
    try:
        data = json.loads(request.data)
        cart = db.users.find_one({ "username":data["Data"]["username"] })
        id = cart["cart"]
        print(cart["cart"])
        user_obj = {user_obj: {} for user_obj in range(len(cart["cart"]))}
        total = 0
        i = 0
        for k in id:
            d = db.products.find_one({ "_id" : ObjectId(k)  })
            user_obj[i]["prod_id"] = k
            user_obj[i]["prod_name"] = d["prod_name"]
            user_obj[i]["prod_value"] = d["prod_value"]
            user_obj[i]["prod_desc"] = d["prod_desc"]
            user_obj[i]["img"] = d["img"]
            user_obj[i]["user_name"] = d["user_name"]
            i = i+1
            total = total + int(d["prod_value"])
        response = jsonify({'ReturnMsg':'Success','user':user_obj}) 
        response.status_code = 200
    except Exception as e:
        print(e)
    return response

#5 ADD TO CART API
@app.route('/api/services/v1/addToCart', methods=['POST', 'GET'])
def get_add_to_cart_api():
    response = jsonify({})
    response.status_code = 404
    try:
        data = json.loads(request.data)
        db.users.update_one( { "username" : data["Data"]["username"] }, { '$addToSet' : { "cart":data["Data"]["prod_id"] } } )
        response = jsonify({'ReturnMsg':'Success'}) 
        response.status_code = 200
    except Exception as e:
        print(e)
    return response

#6 REMOVE FROM CART API
@app.route('/api/services/v1/removeFromCart', methods=['POST', 'GET'])
def get_remove_cart_api():
    response = jsonify({})
    response.status_code = 404
    try:
        data = json.loads(request.data)
        db.users.update_one({'username':data["Data"]["username"] },{ '$pull': { 'cart':data["Data"]["prod_id"] } } )
        response = jsonify({'ReturnMsg':'Success'}) 
        response.status_code = 200
    except Exception as e:
        print(e)
    return response

#7 PUBLISH PRODUCT API
@app.route('/api/services/v1/publishProduct', methods=['POST', 'GET'])
def get_publish_product_api():
    response = jsonify({})
    response.status_code = 404
    try:
        data = json.loads(request.data) #prod_name prod_value prod_desc image
        print(request.files)
        if 'image' not in request.files:
            resp = jsonify({'message' : 'No file part in the request'})
            resp.status_code = 400
            return resp
        file = request.files['image']
        if file.filename == '':
            resp = jsonify({'message' : 'No file selected for uploading'})
            resp.status_code = 400
            return resp
        if file and allowed_file(file.filename):
            print("ALL Good1")
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_PATH, filename))
            db.products.insert({'prod_name': data['prod_name'],'prod_value': data['prod_value'], 'prod_desc': data['prod_desc'], 'img':filename, 'user_name':data['username'] })
        
        else:
            resp = jsonify({'message' : 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
            resp.status_code = 400
            return resp
    except Exception as e:
        print(e)
    response = jsonify({'message' : 'File successfully uploaded'})
    response.status_code = 200
    return response
