from flask import Flask, render_template
import pandas as pd

from finaceManger import fin, SUBSCRIPTION_NAMES

app = Flask(__name__)

@app.route("/")
def index():
    file = "July2024.csv" 
    df = pd.DataFrame(fin(file, SUBSCRIPTION_NAMES), columns=["date", "name", "amount", "category"])
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce") 
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    income = df[df["amount"] > 0]["amount"].sum().round(2)
    expenses = -df[df["amount"] < 0]["amount"].sum().round(2)
    net = (income - expenses).round(2)


    df["month"] = df["date"].dt.to_period("M").astype(str)
    monthly = df.groupby("month")["amount"].sum().reset_index()

    month_labels = monthly["month"].tolist()
    monthly_income = df[df["amount"] > 0].groupby("month")["amount"].sum().reindex(month_labels, fill_value=0).tolist()
    monthly_expenses = (
        df[df["amount"] < 0]
        .groupby("month")["amount"]
        .sum()
        .reindex(month_labels, fill_value=0)
        .mul(-1)              
        .tolist()
    )
    summary = df[df["amount"] < 0].groupby("category")["amount"].sum().reset_index()


    cats = summary["category"].tolist()
    cat_amounts = summary["amount"].abs().round(2).tolist()

    return render_template(
        "index.html",
        summary=summary.to_html(classes="data", index=False),
        income=income,
        expenses=expenses,
        net=net,
        month_labels=month_labels,
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        categories=cats,
        category_amounts=cat_amounts,
    )

if __name__ == "__main__":
    app.run(debug=True)
