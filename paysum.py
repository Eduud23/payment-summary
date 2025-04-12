from flask import Flask, request, jsonify
from flask_cors import CORS
import stripe
import os

app = Flask(__name__)
CORS(app)

# Set your Stripe secret key from environment variable
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

@app.route("/payment-summary", methods=["GET"])
def payment_summary():
    payment_intent_id = request.args.get("payment_intent_id")

    if not payment_intent_id:
        return jsonify({"error": "Missing payment_intent_id"}), 400

    try:
        # Step 1: Retrieve the PaymentIntent
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        # Step 2: Get the latest charge ID
        latest_charge_id = intent.get("latest_charge")

        if not latest_charge_id:
            return jsonify({"error": "No charge found for this PaymentIntent"}), 404

        # Step 3: Retrieve the Charge
        charge = stripe.Charge.retrieve(latest_charge_id)
        card = charge.payment_method_details.card

        return jsonify({
            "amount": charge.amount / 100,
            "currency": charge.currency.upper(),
            "status": charge.status,
            "card_brand": card.brand,
            "card_last4": card.last4,
            "card_exp_month": card.exp_month,
            "card_exp_year": card.exp_year,
            "payment_method_id": charge.payment_method,
            "receipt_url": charge.receipt_url
        })

    except stripe.error.StripeError as e:
        return jsonify({"error": e.user_message or str(e)}), 500
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500

# 🔧 Local dev only: This won't be used on Vercel
if __name__ == "__main__":
    app.run(debug=True, port=5000)
