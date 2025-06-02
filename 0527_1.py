import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import japanize_matplotlib

st.title("📝家計簿分析アプリ📝")
st.write("直近３ヶ月の収入と支出データを入力して，家計の傾向を分析してみよう")

# 分析する項目
items = ["食費🍚", "住居費🏠", "交通費🚃", "通信費🛜", "医療費💊", "水道光熱費🚰"]
num_months = 3 

st.subheader(f"過去{num_months}ヶ月のデータを入力しよう(単位: 円)")

# 収入データ入力↓
st.markdown("#### 収入データを入力しよう")
income_items = ["バイト代",  "仕送り"] 
data_income = {f"{i+1}月": [0] * len(income_items) for i in range(num_months)}
df_income = pd.DataFrame(data_income, index=income_items)

edited_df_income = st.data_editor(
    df_income,
    column_config={
        f"{i+1}月": st.column_config.NumberColumn(
            label=f"{i+1}月",
            min_value=0,
            format="%.0f",
        )
        for i in range(num_months)
    },
    num_rows="fixed",
    height=200, # 高さを調整
    key="income_editor" # キーをユニークにする
)

# 支出データ入力↓
st.markdown("#### 支出データを入力しよう")
data_expenses = {f"{i+1}月": [0] * len(items) for i in range(num_months)}
df_expenses = pd.DataFrame(data_expenses, index=items)

edited_df_expenses = st.data_editor(
    df_expenses,
    column_config={
        f"{i+1}月": st.column_config.NumberColumn(
            label=f"{i+1}月",
            min_value=0,
            format="%.0f",
        )
        for i in range(num_months)
    },
    num_rows="fixed",
    height=400,
    key="expense_editor" # キーをユニークにする
)

if st.button("家計を分析"):
    # 収入と支出のNumPy行列に変換
    income_matrix = edited_df_income.values
    expense_matrix = edited_df_expenses.values

    if income_matrix.shape[1] > 0 and expense_matrix.shape[1] > 0:
        # 支出の分析結果↓
        st.subheader("支出分析結果")
        average_expenses = np.mean(expense_matrix, axis=1)
        st.write("##### 各項目の平均支出")
        for i, item in enumerate(items):
            st.success(f"{item}: {average_expenses[i]:,.0f} 円")

        total_monthly_expenses = np.sum(expense_matrix, axis=0)
        st.write("##### 月ごとの合計支出")
        for i, month_total in enumerate(total_monthly_expenses):
            st.info(f"{i+1}月の合計支出: {month_total:,.0f} 円")
        st.success(f"{num_months}ヶ月間の合計支出: {np.sum(total_monthly_expenses):,.0f} 円")

        # 収入の分析結果↓
        st.subheader("収入分析結果")
        total_monthly_income = np.sum(income_matrix, axis=0)
        st.write("##### 月ごとの合計収入")
        for i, month_total in enumerate(total_monthly_income):
            st.info(f"{i+1}月の合計収入: {month_total:,.0f} 円")
        st.success(f"{num_months}ヶ月間の合計収入: {np.sum(total_monthly_income):,.0f} 円")


        # 収支の計算と表示↓
        st.subheader("月ごとの収支")
        monthly_balance = total_monthly_income - total_monthly_expenses
        for i, balance in enumerate(monthly_balance):
            if balance >= 0:
                st.success(f"{i+1}月の収支: {balance:,.0f} 円 (黒字)")
            else:
                st.error(f"{i+1}月の収支: {balance:,.0f} 円 (赤字)")
        st.success(f"{num_months}ヶ月間の合計収支: {np.sum(monthly_balance):,.0f} 円")


        # 支出の推移グラフ↓
        st.subheader("支出の月ごとの推移")
        fig_expense_trend, ax_expense_trend = plt.subplots(figsize=(10, 6))
        months = [f"{i+1}月" for i in range(num_months)]
        for i, item in enumerate(items):
            ax_expense_trend.plot(months, expense_matrix[i], marker="o", label=item)
        ax_expense_trend.set_xlabel("月")
        ax_expense_trend.set_ylabel("支出額 (円)")
        ax_expense_trend.set_title("各項目の支出推移")
        ax_expense_trend.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        ax_expense_trend.grid(True)
        plt.xticks(rotation=0)
        plt.tight_layout()
        st.pyplot(fig_expense_trend)
        plt.close(fig_expense_trend)

        # 月ごとの合計支出推移グラフ↓
        st.subheader("月ごとの合計支出推移")
        fig_total_expense, ax_total_expense = plt.subplots(figsize=(8, 5))
        ax_total_expense.bar(months, total_monthly_expenses, color="skyblue")
        ax_total_expense.set_xlabel("月")
        ax_total_expense.set_ylabel("合計支出額 (円)")
        ax_total_expense.set_title("月ごとの合計支出推移")
        ax_total_expense.grid(axis="y")
        plt.xticks(rotation=0)
        plt.tight_layout()
        st.pyplot(fig_total_expense)
        plt.close(fig_total_expense)

        # 月ごとの収支推移グラフ↓
        st.subheader("月ごとの収支推移")
        fig_balance, ax_balance = plt.subplots(figsize=(8, 5))
        colors = ['green' if b >= 0 else 'red' for b in monthly_balance] # 黒字は緑、赤字は赤
        ax_balance.bar(months, monthly_balance, color=colors)
        ax_balance.set_xlabel("月")
        ax_balance.set_ylabel("収支 (円)")
        ax_balance.set_title("月ごとの収支推移")
        ax_balance.axhline(0, color='grey', linewidth=0.8) # ゼロライン
        ax_balance.grid(axis="y")
        plt.xticks(rotation=0)
        plt.tight_layout()
        st.pyplot(fig_balance)
        plt.close(fig_balance)

    else:
        st.warning("分析するデータがありません．収入と支出の両方を入力してください．")