from typing import Dict, Any, List
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

# Decorator 
def register_function(name: str):
    def wrapper(func):
        func._register_name = name
        return func
    return wrapper

@register_function("summarize_and_visualize_data")
def summarize_and_visualize_data(payload: Dict[str, Any], secrets: Dict[str, str], event_stream: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Accepts a dataset and returns basic descriptive statistics and visualizations.
    """
    try:
        df = pd.DataFrame(payload.get("data"))

        if df.empty:
            return {"status": "error", "message": "Dataset is empty"}

        # Convert object columns that are likely dates
        for col in df.select_dtypes(include=["object"]):
            try:
                df[col] = pd.to_datetime(df[col], errors='ignore')
            except Exception:
                continue

        # Get descriptive stats
        description = df.describe(include="all").fillna("").to_dict()

        visualizations = []

        # Correlation Matrix
        numeric_cols = df.select_dtypes(include=["number"])
        if numeric_cols.shape[1] >= 2:
            fig, ax = plt.subplots()
            sns.heatmap(numeric_cols.corr(), annot=True, cmap="coolwarm", ax=ax)
            ax.set_title("Correlation Matrix")
            buf = io.BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format="png")
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode("utf-8")
            visualizations.append({
                "column": "Correlation Matrix",
                "plot": img_base64
            })
            plt.close(fig)

        # Prepare plots for each column
        for column in df.columns:
            fig, ax = plt.subplots()
            try:
                if pd.api.types.is_numeric_dtype(df[column]):
                    sns.histplot(df[column].dropna(), kde=True, ax=ax)
                    ax.set_title(f"Histogram of {column}")
                    ax.set_xlabel(column)
                elif pd.api.types.is_categorical_dtype(df[column]) or df[column].dtype == object:
                    df[column].value_counts().plot(kind="bar", ax=ax)
                    ax.set_title(f"Bar Chart of {column}")
                    ax.set_xlabel(column)
                elif pd.api.types.is_datetime64_any_dtype(df[column]):
                    df[column].value_counts().sort_index().plot(ax=ax)
                    ax.set_title(f"Time Series of {column}")
                    ax.set_xlabel(column)
                else:
                    continue  # Skip unsupported types

                buf = io.BytesIO()
                plt.tight_layout()
                plt.savefig(buf, format="png")
                buf.seek(0)
                img_base64 = base64.b64encode(buf.read()).decode("utf-8")
                visualizations.append({
                    "column": column,
                    "plot": img_base64
                })
            except Exception:
                plt.close(fig)
                continue
            plt.close(fig)

        return {
            "status": "success",
            "description": description,
            "visualizations": visualizations
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
