import json
import os

path = "notebooks/01_eda.ipynb"
with open(path, "r") as f:
    nb = json.load(f)

# Find if the cell is already there to avoid duplicates
has_cell = False
for cell in nb['cells']:
    if cell['cell_type'] == 'markdown' and '## 5. Year-on-Year Trend' in ''.join(cell['source']):
        has_cell = True
        break

if not has_cell:
    new_markdown = {
       "cell_type": "markdown",
       "metadata": {},
       "source": [
        "## 5. Year-on-Year Trend (Inflation vs Deflation)\n",
        "We want to observe how the `Closing Rank` changes across different years for the top 5 most popular programs. If the trend is flat, `Year` might not be an important feature. If the ranks are shifting consistently (e.g., CSE cutoffs getting stricter), the model *must* use `Year` as a weighted feature to capture the timeline."
       ]
    }
    
    new_code = {
       "cell_type": "code",
       "execution_count": None,
       "metadata": {},
       "outputs": [],
       "source": [
        "import matplotlib.pyplot as plt\n",
        "import seaborn as sns\n",
        "\n",
        "# 1. Identify the top 5 most common Academic Programs\n",
        "top_5_programs = df['Academic Program Name'].value_counts().head(5).index\n",
        "\n",
        "# 2. Filter the dataframe to only include these top 5 programs\n",
        "trend_df = df[df['Academic Program Name'].isin(top_5_programs)].copy()\n",
        "\n",
        "# 3. We filter to 'OPEN' Seat Type for a clean baseline trend to avoid skew from different quotas\n",
        "trend_df = trend_df[trend_df['Seat Type'] == 'OPEN']\n",
        "\n",
        "# 4. Calculate the average Closing Rank per year for each program\n",
        "yearly_trend = trend_df.groupby(['Year', 'Academic Program Name'])['Closing Rank'].mean().reset_index()\n",
        "\n",
        "# 5. Plot the trend\n",
        "plt.figure(figsize=(14, 8))\n",
        "sns.lineplot(data=yearly_trend, x='Year', y='Closing Rank', hue='Academic Program Name', marker='o', linewidth=2.5)\n",
        "\n",
        "plt.title('YoY Trend of Average Closing Ranks (OPEN) for Top 5 Programs', fontsize=16)\n",
        "plt.xlabel('Year', fontsize=12)\n",
        "plt.ylabel('Average Closing Rank', fontsize=12)\n",
        "# Move legend outside the plot so it doesn't overlap lines\n",
        "plt.legend(title='Academic Program', bbox_to_anchor=(1.05, 1), loc='upper left')\n",
        "plt.grid(True, linestyle='--', alpha=0.7)\n",
        "plt.tight_layout()\n",
        "plt.show()"
       ]
    }
    
    # Remove empty cells at the end if any
    while nb['cells'] and nb['cells'][-1]['source'] == []:
        nb['cells'].pop()
        
    nb['cells'].extend([new_markdown, new_code])
    
    with open(path, "w") as f:
        json.dump(nb, f, indent=1)
    print("Successfully appended YoY trend cells.")
else:
    print("Cells already exist.")
