from flask import Flask, render_template
import pandas as pd

from finaceManger import fin, SUBSCRIPTION_NAMES

app = Flask(__name__)

@app.route("/")
def index():
    file = "Jully2024.csv" 
    df = pd.DataFrame(fin(file, SUBSCRIPTION_NAMES), columns=["date", "name", "amount", "category"])
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # ----- Summary -----
    summary = df.groupby("category")["amount"].sum().reset_index()
    total_income = df[df["amount"] > 0]["amount"].sum().round(2)
    total_expenses = -df[df["amount"] < 0]["amount"].sum().round(2)
    net = (total_income - total_expenses).round(2)

    # ----- Monthly Summary -----
    df["month"] = df["date"].dt.to_period("M").astype(str)
    monthly = df.groupby("month")["amount"].sum().reset_index()

    monthly_labels = monthly["month"].tolist()
    monthly_income = df[df["amount"] > 0].groupby("month")["amount"].sum().reindex(monthly_labels, fill_value=0).tolist()
    monthly_expenses = -df[df["amount"] < 0].groupby("month")["amount"].sum().reindex(monthly_labels, fill_value=0)
    monthly_expenses = (
        df[df["amount"] < 0]
        .groupby("month")["amount"]
        .sum()
        .reindex(monthly_labels, fill_value=0)
        .mul(-1)              
        .tolist()
    )
    expense_summary = df[df["amount"] < 0].groupby("category")["amount"].sum().reset_index()


    # ----- Category Pie -----
    categories = expense_summary["category"].tolist()

    category_amounts = expense_summary["amount"].abs().round(2).tolist()

    return render_template(
        "index.html",
        summary=summary.to_html(classes="data", index=False),
        total_income=total_income,
        total_expenses=total_expenses,
        net=net,
        monthly_labels=monthly_labels,
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        categories=categories,
        category_amounts=category_amounts,
    )

if __name__ == "__main__":
    app.run(debug=True)
