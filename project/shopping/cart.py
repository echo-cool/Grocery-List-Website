from flask import Blueprint, Response
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_user, login_required, current_user, logout_user

from project import app
from project.models import ItemModel
from project.models.Cart import Cart
from project.models.ItemModel import Item
from project.models.UserModel import User
from project.utils import buyer_required

blueprint = Blueprint("cart", __name__, static_folder="../static")


@blueprint.route("/cart/remove", methods=["GET", "POST"])
@login_required
@buyer_required
def remove_from_cart() -> Response:
    itemID: int = request.form.get('itemID')
    user: User = current_user
    cart_entry: Cart = Cart.query.filter_by(item_id=itemID, user_id=user.id).first()

    if cart_entry:
        cart_entry.delete()

    flash("Removed Successfully")
    return redirect(url_for('cart.shopping_cart'))


@blueprint.route("/cart/add", methods=["POST"])
@login_required
@buyer_required
def add_to_cart() -> Response:
    itemID: int = request.form.get('itemID')
    itemCount: int = request.form.get('itemCount')
    user: User = current_user
    item: Item = Item.get_by_id(itemID)
    cart_entry: Cart = Cart.query.filter_by(item_id=itemID, user_id=user.id).first()
    if cart_entry:
        current_count: int = cart_entry.count
        cart_entry.update(
            count=int(current_count) + int(itemCount)
        )
    else:
        Cart.create(
            item_id=itemID,
            user_id=user.id,
            count=itemCount
        )

    flash("Successfully added " + str(itemCount) + " " + str(item.name) + " to your cart !")
    return redirect(url_for('item.details', itemID=itemID))


@blueprint.route("/cart/set", methods=["POST"])
@login_required
@buyer_required
def set_to_cart() -> Response:
    itemID: int = request.form.get('itemID')
    itemCount: int = request.form.get('itemCount')
    user: User = current_user
    item: Item = Item.get_by_id(itemID)
    cart_entry: Cart = Cart.query.filter_by(item_id=itemID, user_id=user.id).first()
    if cart_entry:
        if int(itemCount) <= 0:
            cart_entry: Cart = Cart.query.filter_by(item_id=itemID, user_id=user.id).first()
            if cart_entry:
                cart_entry.delete()
            flash("Removed Successfully")
            return redirect(url_for('cart.shopping_cart', itemID=itemID))
        cart_entry.update(
            count=int(itemCount)
        )
    else:
        Cart.create(
            item_id=itemID,
            user_id=user.id,
            count=itemCount
        )

    return redirect(url_for('cart.shopping_cart', itemID=itemID))


@blueprint.route("/cart", methods=["GET", "POST"])
@login_required
@buyer_required
def shopping_cart() -> str:
    user: User = current_user
    cart: Cart = Cart.query.filter_by(user_id=user.id).all()
    res: dict = {}
    total_price: int = 0
    for i in cart:
        shop_user_id: int = i.get_shop_userID()
        item_id: int = i.item_id
        item: Item = Item.get_by_id(item_id)
        shopper: User = User.get_by_id(shop_user_id)
        item.count = i.count
        total_price += item.price * i.count

        if shopper in res.keys():
            res[shopper].append(item)
        else:
            res[shopper] = [item]

    return render_template("shopping/shopping_cart.html", cart_dict=res, total_price=total_price)