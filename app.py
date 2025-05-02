from flask import Flask, render_template, request
from datetime import datetime
import pandas as pd

# import pymysql
from pm25 import get_pm25_data_from_mysql, update_db, get_pm25_data_by_site
import json

app = Flask(__name__)


@app.route("/pm25-data-site")
def pm25_data_by_site():
    county = request.args.get("county")
    site = request.args.get("site")

    if not county or not site:
        result = json.dumps({"error": "縣市跟站點名稱不能為空!"}, ensure_ascii=False)
    else:
        columns, datas = get_pm25_data_by_site(county, site)
        df = pd.DataFrame(datas, columns=columns)
        # 轉換字串時間格式
        date = df["datacreationdate"].apply(lambda x: x.strftime("%Y-%m-%d %H"))
        data = {
            "county": county,
            "site": site,
            "x_data": date.to_list(),
            "y_data": df["pm25"].to_list(),
        }
        result = json.dumps(data, ensure_ascii=False)
    return result


# @app.route("/filter", methods=["POST"])
# def filter_data():
#     # args => form
#     county = request.form.get("county")
#     columns, datas = get_pm25_data_from_mysql()
#     df = pd.DataFrame(datas, columns=columns)
#     # 取得特定縣市的資料
#     df1 = df.groupby("county").get_group(county).groupby("site")["pm25"].mean()
#     print(df1)
#     return {"county": county}


# 更新資料庫
@app.route("/update-db")
def update_pm25_db():
    count, message = update_db()
    nowtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = json.dumps(
        {"時間": nowtime, "更新筆數": count, "結果": message}, ensure_ascii=False
    )
    return result


@app.route("/")
def index():
    # 取得資料庫最新資料
    columns, datas = get_pm25_data_from_mysql()
    # print(datas)
    # 取出不同縣市
    df = pd.DataFrame(datas, columns=columns)
    # 排序縣市
    counties = sorted(df["county"].unique().tolist())
    print(counties)
    # return render_template(
    # "index.html", columns=columns, datas=datas, counties=counties
    # )

    # 選取縣市後的資料 (預設All)
    county = request.args.get("county", "ALL")
    if county == "ALL":
        df1 = df.groupby("county")["pm25"].mean().reset_index()
        x_data = df1["county"].to_list()

    else:
        # 取得特定縣市的資料
        df = df.groupby("county").get_group(county)
        x_data = df["site"].to_list()

    y_data = df["pm25"].to_list()
    columns = df.columns.tolist()
    datas = df.values.tolist()
    # print(columns, datas)
    # 繪製所需資料

    return render_template(
        "index.html",
        columns=columns,
        datas=datas,
        counties=counties,
        selected_county=county,
        x_data=x_data,
        y_data=y_data,
    )


# @app.route("/books")
# def books_page():
#     # return f"<h1>Hello World!</h1><br>{datetime.now()}"
#     #
#     books = {1: "Python book", 2: "Java book", 3: "Flask book"}
#     books = [
#         {
#             "name": "Python book",
#             "price": 299,
#             "image_url": "https://im2.book.com.tw/image/getImage?i=https://www.books.com.tw/img/CN1/136/11/CN11361197.jpg&v=58096f9ck&w=348&h=348",
#         },
#         {
#             "name": "Java book",
#             "price": 399,
#             "image_url": "https://im1.book.com.tw/image/getImage?i=https://www.books.com.tw/img/001/087/31/0010873110.jpg&v=5f7c475bk&w=348&h=348",
#         },
#         {
#             "name": "C# book",
#             "price": 499,
#             "image_url": "https://im1.book.com.tw/image/getImage?i=https://www.books.com.tw/img/001/036/04/0010360466.jpg&v=62d695bak&w=348&h=348",
#         },
#     ]
#     # books = []
#     if not books:
#         print("販售完畢，目前無書籍!")
#     # for key in books:
#     # print(key, books[key])
#     for book in books:
#         print(book["name"])
#         print(book["price"])
#         print(book["image_url"])

#     username = "jerry"
#     nowtime = datetime.now().strftime("%Y-%m-%d")
#     print(username, nowtime)
#     return render_template("books.html", name=username, now=nowtime, books=books)


# @app.route("/bmi")
# def get_bmi():
#     # args => GET
#     height = eval(request.args.get("height"))
#     weight = eval(request.args.get("weight"))
#     print(height, weight)
#     bmi = round(weight / (height / 100) ** 2, 2)
#     # return render_template("bmi.html", height=height, weight=weight, bmi=bmi)
#     return render_template("bmi.html", **locals())


# @app.route("/pm25-data")
# def get_pm25_data():
#     api_url = "https://data.moenv.gov.tw/api/v2/aqx_p_02?api_key=540e2ca4-41e1-4186-8497-fdd67024ac44&limit=1000&sort=datacreationdate%20desc&format=CSV"
#     df = pd.read_csv(api_url)
#     df["datacreationdate"] = pd.to_datetime(df["datacreationdate"])
#     df1 = df.dropna()
#     return df1.values.tolist()


if __name__ == "__main__":
    app.run(debug=True)
