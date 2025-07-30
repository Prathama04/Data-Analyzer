import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re
from sklearn.feature_selection import mutual_info_classif
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
from scipy.stats import entropy, ttest_ind, f_oneway
from typing import List, Optional
import traceback # Keep traceback here for logging within the class

def is_id_like(col_name: str) -> bool:
    # Split by non-alphanumeric characters like _, (, ), etc.
    tokens = re.split(r'[\W_]+', col_name.lower())
    id_like_tokens = {'id', 'uuid', 'number', 'code', 'serial', 'sku', 'name'}
    return any(token in id_like_tokens for token in tokens)

def read_excel_clean(path: str, sheet_name: str = 0) -> pd.DataFrame:
    # Step 1: Read Excel
    df = pd.read_excel(path, sheet_name=sheet_name)
    n_rows=len(df)
    # Step 2: Drop completely empty rows/columns
    df.dropna(how='all', inplace=True)
    df.dropna(axis=1, how='all', inplace=True)
    skip_cols = set()
    # for col in df.columns:
    #     if is_id_column(col):
    #         skip_cols.add(col)
    df = df[[col for col in df.columns if col not in skip_cols]]
    # Step 3: Clean column names
    df.columns = [
        str(col).strip().lower().replace(' ', '_').replace('\n', '_')
        for col in df.columns
    ]

    # Step 4: Try to infer datetime columns
    for col in df.columns:
        if df[col].dtype == object:
            try:
                parsed = pd.to_datetime(df[col], errors='coerce', utc=False)
                if parsed.notna().sum() > 0.6 * len(parsed):
                    df[col] = parsed
            except Exception:
                continue

    # Step 5: Convert object-like numerics to float
    for col in df.select_dtypes(include='object').columns:
        try:
            numeric_series = pd.to_numeric(df[col], errors='coerce')
            if numeric_series.notna().sum() > 0.6 * len(numeric_series):
                df[col] = numeric_series
        except Exception:
            continue

    # Step 6: Fill missing values smartly
    for col in df.columns:
        if df[col].isna().sum() == 0:
            continue

        if pd.api.types.is_numeric_dtype(df[col]):
            # Interpolate first, fallback to median
            df[col] = df[col].interpolate(method='linear', limit_direction='both')
            df[col] = df[col].fillna(df[col].median())
        
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].fillna(method='ffill').fillna(method='bfill')

        elif isinstance(df[col].dtype, pd.CategoricalDtype) or df[col].dtype == object:
            mode_val = df[col].mode().iloc[0] if not df[col].mode().empty else "Unknown"
            df[col] = df[col].fillna(mode_val)

    return df

def profile_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    profile = []

    for col in df.columns:
        data = df[col]
        dtype = str(data.dtype)
        missing_pct = data.isna().mean() * 100
        unique_vals = data.nunique(dropna=True)

        top_values = (
            data.value_counts(dropna=True)
            .head(5)
            .to_dict()
        )

        col_profile = {
            "column": col,
            "dtype": dtype,
            "missing_%": round(missing_pct, 2),
            "unique_values": unique_vals,
            "top_values": top_values
        }

        if pd.api.types.is_numeric_dtype(data):
            col_profile.update({
                "min": data.min(),
                "max": data.max(),
                "mean": data.mean(),
                "median": data.median(),
                "std": data.std()
            })

        elif pd.api.types.is_datetime64_any_dtype(data):
            col_profile.update({
                "min_date": data.min(),
                "max_date": data.max(),
                "range_days": (data.max() - data.min()).days
            })

        profile.append(col_profile)

    return pd.DataFrame(profile)

def choose_best_period(df: pd.DataFrame, datetime_col: str, min_bins=6, max_bins=60) -> str:
    options = ["D", "W", "M", "Q", "Y"]
    n_unique = {}
    for freq in options:
        try:
            periods = df[datetime_col].dt.to_period(freq)
            n_periods = periods.nunique()
            n_unique[freq] = n_periods
        except Exception:
            continue

    # Filter options that fall within a reasonable bin count
    viable = {k: v for k, v in n_unique.items() if min_bins <= v <= max_bins}
    
    if viable:
        # Choose the highest resolution viable period (e.g., prefer 'M' over 'Q')
        return min(viable, key=lambda k: options.index(k))
    else:
        # Fallback to the period that gives the closest number of bins to min_bins
        return min(n_unique, key=lambda k: abs(n_unique[k] - min_bins))

def is_duration_like(col: pd.Series) -> bool:
    return col.dropna().between(0.1, 24).mean() > 0.7 and col.std() < 5

def is_percentage_like(col: pd.Series) -> bool:
    return col.dropna().between(0.001, 1.5).mean() > 0.8 or '%' in col.name.lower()

def format_time_from_hours(hours):
    seconds = int(hours * 3600)
    return f"{seconds // 3600}:{(seconds % 3600) // 60:02}:{seconds % 60:02}"

def format_seconds_to_hhmmss(seconds):
    if pd.isnull(seconds):
        return "N/A"
    seconds = int(round(seconds * 3600))  # hours → seconds
    return f"{seconds//3600}:{(seconds%3600)//60:02}:{seconds%60:02}"

def is_valid_datetime_column(series: pd.Series) -> bool:
    if not pd.api.types.is_datetime64_any_dtype(series):
        return False
    if pd.api.types.is_timedelta64_dtype(series):
        return False
    if series.dt.date.nunique() < 5:
        return False
    if (series.dt.time != pd.to_datetime('00:00:00').time()).all():
        return False
    return True

def convert_hhmmss_to_timedelta(series: pd.Series) -> pd.Series:
    def parse_duration(val):
        if pd.isnull(val):
            return np.nan
        if isinstance(val, (pd.Timedelta, np.timedelta64)):
            return val
        if isinstance(val, str):
            match = re.match(r'^(\d{1,2}):(\d{2})(?::(\d{2}))?$', val.strip())
            if match:
                h, m, s = match.groups()
                h = int(h)
                m = int(m)
                s = int(s or 0)
                return pd.Timedelta(hours=h, minutes=m, seconds=s)
        return np.nan

    converted = series.apply(parse_duration)
    if converted.notna().sum() > 0.6 * len(series):
        return converted
    return series  # fallback if most couldn't be parsed

def get_top_performers(df: pd.DataFrame, top_numeric_cols: list) -> dict:
    top_performers = {}

    # Step 1: Try to find a name/id column
    name_id_cols = [col for col in df.columns if df[col].dtype == object and is_id_like(col)]
    group_col = name_id_cols[0] if name_id_cols else None

    if group_col:
        for num_col in top_numeric_cols:
            grp = df.groupby(group_col)[num_col].sum()
            top = grp.idxmax()
            top_performers[f"top_{group_col}_by_{num_col}"] = {
                "name": top,
                "total": float(grp[top])
            }
    else:
        # Step 2: Use best-separating categorical column instead (up to 3)
        cat_cols = [
            col for col in df.select_dtypes(include='object').columns
            if 2 < df[col].nunique() < min(len(df) // 4, 30)
        ]
        separation_scores = {}
        for cat in cat_cols:
            score = 0
            for num in top_numeric_cols:
                try:
                    means = df.groupby(cat)[num].mean()
                    score += means.std()
                except:
                    continue
            if score > 0:
                separation_scores[cat] = score

        best_cat_cols = sorted(separation_scores, key=separation_scores.get, reverse=True)[:3]

        for cat in best_cat_cols:
            for num in top_numeric_cols:
                try:
                    grp = df.groupby(cat)[num].sum()
                    top = grp.idxmax()
                    top_performers[f"top_{cat}_by_{num}"] = {
                        "name": top,
                        "total": float(grp[top])
                    }
                except:
                    continue

    return top_performers

def detect_trends(
    df: pd.DataFrame,
    date_col: str = None,
    top_numeric_cols: list = []
) -> dict:
    trend_insights = {}
    df = df.copy()

    # 1. Temporal trend & seasonality (if date exists)
    if date_col and date_col in df.columns and pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df = df.sort_values(by=date_col)
        df['_date_num'] = (df[date_col] - df[date_col].min()).dt.days

        for col in top_numeric_cols:
            y = df[col].dropna()
            x = df['_date_num'].loc[y.index].values.reshape(-1, 1)
            if len(x) < 5:
                continue

            model = LinearRegression().fit(x, y)
            slope = model.coef_[0]
            direction = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
            trend_insights[col] = {"overall_trend": direction}

            # Seasonality (by quarter)
            df["quarter"] = df[date_col].dt.to_period("Q")
            seasonal = df.groupby("quarter")[col].mean()
            if len(seasonal) >= 1:
                top_q = seasonal.idxmax().strftime("Q%q %Y")
                bottom_q = seasonal.idxmin().strftime("Q%q %Y")
                trend_insights[col]["seasonal_pattern"] = {
                    "peak": top_q,
                    "low": bottom_q
                }

    # 2. Conditional effects
    conditional_effects = []

    # 2A. Numeric → Numeric (quantile-based t-test)
    condition_candidates = [
        col for col in df.select_dtypes(include='number').columns
        if df[col].nunique() > 5 and not df[col].isin([0, 1]).all()
    ]

    for cond in condition_candidates:
        high = df[df[cond] > df[cond].quantile(0.8)]
        low = df[df[cond] <= df[cond].quantile(0.8)]

        for target in top_numeric_cols:
            if target == cond or target not in df.columns:
                continue
            mean_high = high[target].mean()
            mean_low = low[target].mean()

            if pd.notnull(mean_high) and pd.notnull(mean_low) and len(high[target].dropna()) >= 5 and len(low[target].dropna()) >= 5:
                stat, pval = ttest_ind(high[target].dropna(), low[target].dropna(), equal_var=False)
                pct_change = (mean_high - mean_low) / abs(mean_low + 1e-6) * 100

                if pval < 0.05 and abs(pct_change) > 20:
                    conditional_effects.append({
                        "condition": f"{cond} > 80th percentile",
                        "target": target,
                        "effect": f"{pct_change:.1f}% {'increase' if pct_change > 0 else 'decrease'}",
                        "p_value": f"{pval:.4f}"
                    })

    # 2B. Categorical → Numeric (ANOVA)
    cat_cols = [
        col for col in df.select_dtypes(include='object').columns
        if not is_id_like(col) and 2 < df[col].nunique() < 25
    ]

    for cat in cat_cols:
        for target in top_numeric_cols:
            if target not in df.columns:
                continue

            groups = [group.dropna().values for _, group in df.groupby(cat)[target]]
            if len(groups) < 2 or any(len(g) < 3 for g in groups):
                continue

            stat, pval = f_oneway(*groups)
            if pval < 0.05:
                # Optionally: get category with max mean
                means = df.groupby(cat)[target].mean()
                best = means.idxmax()
                worst = means.idxmin()
                diff_pct = (means.max() - means.min()) / abs(means.min() + 1e-6) * 100

                if abs(diff_pct) > 20:
                    conditional_effects.append({
                        "condition": f"{cat} category affects {target}",
                        "target": target,
                        "effect": f"{diff_pct:.1f}% range across categories",
                        "best": best,
                        "worst": worst,
                        "p_value": f"{pval:.4f}"
                    })

        if conditional_effects:
            # Compute a composite score: abs(effect size) × significance
            def effect_score(e):
                try:
                    magnitude = abs(float(re.findall(r"[-+]?\d*\.\d+|\d+", e["effect"])[0]))
                    pval = float(e.get("p_value", 1))
                    score = magnitude * -np.log10(pval + 1e-10)
                    return score
                except:
                    return 0

            conditional_effects.sort(key=effect_score, reverse=True)
            trend_insights["conditional_effects"] = conditional_effects[:5]  # Top 5 only


    return trend_insights

def generate_insights(
    df: pd.DataFrame,
    name_col: Optional[str] = None,
    top_numeric_cols: List[str] = None,
    top_categorical_cols: List[str] = None
) -> dict:
    insights = {}
    df = df.copy()
    df = df.dropna(how="all")
    num_df = df.select_dtypes(include='number')
    cat_df = df.select_dtypes(include='object')
    date_col = None
    for col in df.columns:
        if is_valid_datetime_column(df[col]):
            date_col = col
            break
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = convert_hhmmss_to_timedelta(df[col])

    insights["overview"] = {
        "rows": len(df),
        "columns": df.shape[1],
        "missing_columns": [col for col in df.columns if df[col].isna().any()]
    }

    if date_col:
        insights["overview"]["date_range"] = {
            "start": str(df[date_col].min().date()),
            "end": str(df[date_col].max().date())
        }

    # Infer top columns
    excluded_cols = [col for col in df.columns if is_id_like(col)]
    print("excluded cols:\n",excluded_cols)
    if not top_numeric_cols:
        #print("\n\n",num_df)
        top_numeric_cols = [col for col in num_df.var().sort_values(ascending=False).index if col not in excluded_cols][:5]


    if not top_categorical_cols:
        scores = {}
        for col in cat_df.columns:
            vc = df[col].value_counts(normalize=True)
            # print(col, len(vc))
            if 2 < len(vc) < 50:
                scores[col] = entropy(vc)
        sorted_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_categorical_cols = [col for col, _ in sorted_cats[:5] if col not in excluded_cols]

    insights["top_columns"] = top_numeric_cols + top_categorical_cols

    # Summary Stats
    insights["summary_stats"] = {
        col: {
            "total": float(df[col].sum()),
            "mean": float(df[col].mean()),
            "median": float(df[col].median())
        } for col in top_numeric_cols
    }

    # Derived Ratios
    # if len(top_numeric_cols) >= 2:
    #     a, b = top_numeric_cols[0], top_numeric_cols[1]
    #     total_a, total_b = df[a].sum(), df[b].sum()
    #     if total_a and total_b:
    #         insights["ratios"] = {
    #             f"{b}_as_pct_of_{a}": round(100 * total_b / total_a, 2)
    #         }

    top_performers = get_top_performers(df, top_numeric_cols)
    if top_performers:
        insights["top_performers"] = top_performers

    # General Trends (📈 Trends)
    insights["trends"] = detect_trends(df, date_col, top_numeric_cols)
    extended = generate_extended_insights(df, name_col, top_numeric_cols)
    insights.update(extended)
    return insights

def generate_extended_insights(
    df: pd.DataFrame,
    name_col: Optional[str] = None,
    top_numeric_cols: List[str] = None
) -> dict:
    insights = {}
    df = df.copy()
    df = df.dropna(how="all")

    if not name_col:
        name_col = next((col for col in df.columns if df[col].dtype == object and df[col].nunique() == len(df)), None)

    num_df = df.select_dtypes(include='number')
    if not top_numeric_cols:
        top_numeric_cols = num_df.var().sort_values(ascending=False).head(10).index.tolist()

    high_level = {}
    metric_insights = {}
    observations = []
    distribution_summary = {}

    for col in top_numeric_cols:
        series = df[col].dropna()
        if series.empty:
            continue

        stats = {
            "mean": series.mean(),
            "median": series.median(),
            "min": series.min(),
            "max": series.max(),
            "std": series.std()
        }

        if is_percentage_like(series):
            stats = {k: round(100 * v, 2) for k, v in stats.items()}
            high_level[f"Average {col}"] = f"{stats['mean']}%"
            distribution_summary[col] = f"Most values between {stats['min']}% and {stats['max']}%"
        elif is_duration_like(series):
            high_level[f"Average {col}"] = format_time_from_hours(stats['mean'])
            distribution_summary[col] = f"Most values between {format_time_from_hours(stats['min'])} and {format_time_from_hours(stats['max'])}"
        else:
            high_level[f"Average {col}"] = round(stats['mean'], 2)
            distribution_summary[col] = f"Most values between {stats['min']:.2f} and {stats['max']:.2f}"

        if name_col:
            best = df.loc[series.idxmax()][name_col]
            worst = df.loc[series.idxmin()][name_col]
            metric_insights[col] = {
                "Best Performer": {"name": best, "value": round(series.max(), 2)},
                "Worst Performer": {"name": worst, "value": round(series.min(), 2)}
            }

            if is_percentage_like(series):
                observations.append(f"{best} had the highest {col} at {round(series.max()*100, 1)}%.")
                observations.append(f"{worst} had the lowest {col} at {round(series.min()*100, 1)}%.")
            elif is_duration_like(series):
                observations.append(f"{best} had the longest {col}: {format_time_from_hours(series.max())}.")
                observations.append(f"{worst} had the shortest {col}: {format_time_from_hours(series.min())}.")
            else:
                observations.append(f"{best} scored highest in {col} ({round(series.max(), 2)}).")
                observations.append(f"{worst} scored lowest in {col} ({round(series.min(), 2)}).")

    insights["high_level_summary"] = high_level
    if name_col:
        insights["per_metric_performance"] = metric_insights
    insights["observations"] = observations
    insights["distribution_highlights"] = distribution_summary

    return insights

def generate_important_plots(df: pd.DataFrame, output_dir: str = "important_plots", target_cols: list = None, max_plots: int = 3):
    os.makedirs(output_dir, exist_ok=True)
    sns.set(style="whitegrid")
    df = df.copy()
    plots_made = 0

    # -- Helper: Detect ID-like columns
    def is_probably_identifier(col: pd.Series) -> bool:
        name = col.name.lower()
        if any(kw in name for kw in ['id', 'uuid', 'name', 'code', 'number', 'email']):
            return True
        if pd.api.types.is_string_dtype(col) and col.nunique() > 0.9 * len(col):
            return True
        return False

    id_like_cols = [col for col in df.columns if is_probably_identifier(df[col])]
    df.drop(columns=id_like_cols, inplace=True, errors='ignore')

    # -- Auto-pick target columns if not provided
    if not target_cols:
        # Pick numeric targets: high std dev, excluding timedelta
        num_candidates = df.select_dtypes(include=['number']).std().sort_values(ascending=False)
        top_numeric = num_candidates[num_candidates > 0].head(2).index.tolist()

        # Pick categorical targets: low to mid cardinality
        cat_candidates = [
            col for col in df.select_dtypes(include='object')
            if 2 < df[col].nunique() < 15
        ]
        cat_candidates = cat_candidates[:1]  # Limit to 1 categorical

        target_cols = top_numeric + cat_candidates
    else:
        target_cols = [col for col in target_cols if col in df.columns]

    # -- Identify potential predictors
    num_cols = df.select_dtypes(include=['number']).columns.difference(target_cols).tolist()
    cat_cols = df.select_dtypes(include='object').columns.difference(target_cols).tolist()

    # -- Scatter or Box plots
    for target in target_cols:
        if plots_made >= max_plots:
            break

        y = df[target]
        if pd.api.types.is_numeric_dtype(y):
            corrs = df[num_cols].corrwith(y).abs().sort_values(ascending=False)
            for predictor in corrs.head(2).index:
                plt.figure(figsize=(6, 4))
                sns.scatterplot(x=df[predictor], y=y)
                plt.title(f"{target} vs {predictor}")
                plt.tight_layout()
                plt.savefig(f"{output_dir}/scatter_{target}_vs_{predictor}.png")
                plt.close()
                plots_made += 1
                if plots_made >= max_plots:
                    break
        else:
            le = LabelEncoder()
            y_encoded = le.fit_transform(y.astype(str))
            if num_cols:
                mi_scores = mutual_info_classif(df[num_cols].fillna(0), y_encoded)
                top_predictors = [num_cols[i] for i in np.argsort(mi_scores)[::-1][:2]]
                for predictor in top_predictors:
                    plt.figure(figsize=(6, 4))
                    sns.boxplot(x=y, y=df[predictor])
                    plt.title(f"{predictor} by {target}")
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    plt.savefig(f"{output_dir}/box_{predictor}_by_{target}.png")
                    plt.close()
                    plots_made += 1
                    if plots_made >= max_plots:
                        break

    # -- Time trend plot (use proper datetime only)
    if plots_made < max_plots:
        date_col = None
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]) and not pd.api.types.is_timedelta64_dtype(df[col]):
                date_col = col
                break

        if date_col:
            df_sorted = df.sort_values(by=date_col)
            for target in target_cols:
                if pd.api.types.is_numeric_dtype(df[target]):
                    plt.figure(figsize=(8, 4))
                    plt.plot(df_sorted[date_col], df_sorted[target])
                    plt.title(f"{target} over time")
                    plt.xlabel("Date")
                    plt.ylabel(target)
                    plt.tight_layout()
                    plt.savefig(f"{output_dir}/time_trend_{target}.png")
                    plt.close()
                    plots_made += 1
                    if plots_made >= max_plots:
                        break

    # -- Distribution plots (fallback)
    if plots_made == 0:
        for col in df.select_dtypes(include='number').columns[:3]:
            plt.figure(figsize=(6, 4))
            sns.histplot(df[col].dropna(), kde=True)
            plt.title(f"Distribution of {col}")
            plt.tight_layout()
            plt.savefig(f"{output_dir}/dist_{col}.png")
            plt.close()
            plots_made += 1
            if plots_made >= max_plots:
                break

    # -- Correlation heatmap (last resort)
    if plots_made == 0 and len(df.select_dtypes(include='number').columns) >= 3:
        corr = df.select_dtypes(include='number').corr()
        plt.figure(figsize=(6, 5))
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f')
        plt.title("Numeric Correlation Heatmap")
        plt.tight_layout()
        plt.savefig(f"{output_dir}/correlation_heatmap.png")
        plt.close()
        plots_made += 1

def format_insights_natural_language(insights: dict) -> str:
    lines = []

    # High-Level Summary
    hl = insights.get("high_level_summary", {})
    if hl:
        lines.append("**High-Level Summary**")
        for k, v in hl.items():
            if isinstance(v, (float, int)) and "hour" in k:
                v = format_seconds_to_hhmmss(v)
            lines.append(f"- {k.replace('_', ' ').title()}: {v}")
        lines.append("")

    # Top Performers
    tp = insights.get("top_performers", {})
    if tp:
        lines.append("**Top Performers**")
        for label, data in tp.items():
            metric = label.split("_by_")[-1].replace('_', ' ').title()
            performer = data["name"]
            value = round(data["total"], 2)
            lines.append(f"- Top {metric}: **{performer}** ({value})")
        lines.append("")

    # Trends
    trends = insights.get("trends", {})
    if trends:
        lines.append("**Trends**")
        for metric, info in trends.items():
            if not isinstance(info, dict):
                continue  # skip non-dict entries like conditional_effects
            name = metric.replace('_', ' ').title()
            trend = info.get("overall_trend", "stable")
            seasonal = info.get("seasonal_pattern")
            summary = f"- {name} Trend: {trend.capitalize()}"
            if seasonal:
                summary += f", peaks in {seasonal['peak']}, lows in {seasonal['low']}"
            lines.append(summary)

        # Conditional Effects
        conds = trends.get("conditional_effects", [])
        if conds:
            lines.append("")
            lines.append("**Conditional Effects**")
            for c in conds:
                condition = c["condition"]
                target = c["target"].replace('_', ' ').title()
                effect = c["effect"]
                lines.append(f"- When `{condition}`, it causes **{effect}** in `{target}`.")
        lines.append("")

    # Observations (optional for future)
    obs = insights.get("observations", [])
    if obs:
        lines.append(" **Observations**")
        for o in obs:
            lines.append(f"- {o}")
        lines.append("")

    # Distribution Highlights
    dist = insights.get("distribution_highlights", {})
    if dist:
        lines.append("**Distribution Highlights**")
        for k, v in dist.items():
            lines.append(f"- {k.replace('_', ' ').title()}: {v}")
        lines.append("")

    return "\n".join(lines)



# --- Summarizer Class ---
class Summarizer:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy() # Work on a copy to avoid modifying the original DF
        # Initial cleaning might be done here or assumed to be done before passing DF
        self.df = self._perform_essential_cleaning(self.df)

    def _perform_essential_cleaning(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies essential cleaning steps to the DataFrame,
        similar to parts of read_excel_clean, but suitable for an already loaded DF.
        """
        df.columns = [
            str(col).strip().lower().replace(' ', '_').replace('\n', '_')
            for col in df.columns
        ]
        
        # Convert object-like numerics and datetimes
        for col in df.columns:
            if df[col].dtype == object:
                # Try datetime conversion
                try:
                    parsed = pd.to_datetime(df[col], errors='coerce', utc=False)
                    if parsed.notna().sum() > 0.6 * len(parsed):
                        df[col] = parsed
                        continue # Move to next column if successful
                except Exception:
                    pass
                # Try numeric conversion
                try:
                    numeric_series = pd.to_numeric(df[col], errors='coerce')
                    if numeric_series.notna().sum() > 0.6 * len(numeric_series):
                        df[col] = numeric_series
                except Exception:
                    pass

        # Fill missing values smartly
        for col in df.columns:
            if df[col].isna().sum() == 0:
                continue

            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].interpolate(method='linear', limit_direction='both')
                df[col] = df[col].fillna(df[col].median())
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].fillna(method='ffill').fillna(method='bfill')
            elif isinstance(df[col].dtype, pd.CategoricalDtype) or df[col].dtype == object:
                mode_val = df[col].mode().iloc[0] if not df[col].mode().empty else "Unknown"
                df[col] = df[col].fillna(mode_val)
        return df


    def get_summary(self, output_plot_dir: str = "summary_plots") -> tuple[str, list]:
        """
        Generates summary insights and plots.
        Returns: Tuple of (summary_text: str, list_of_plot_paths: list[str])
        """
        try:
            # Ensure plots directory exists
            os.makedirs(output_plot_dir, exist_ok=True)
            
            # Clear previous plots
            for f in os.listdir(output_plot_dir):
                if f.endswith(".png"):
                    os.remove(os.path.join(output_plot_dir, f))

            # Generate insights
            insights = generate_insights(self.df)
            summary_text = format_insights_natural_language(insights)

            # Generate plots
            generate_important_plots(self.df, output_dir=output_plot_dir)
            
            plot_paths = [os.path.join(output_plot_dir, f) for f in os.listdir(output_plot_dir) if f.endswith(".png")]
            plot_paths.sort() # Ensure consistent order
            
            return summary_text, plot_paths
        except Exception as e:
            traceback.print_exc()
            return f"Error generating summary: {e}", []