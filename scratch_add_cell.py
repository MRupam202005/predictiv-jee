import json
import os

path = "notebooks/02_prototyping.ipynb"
with open(path, "r") as f:
    nb = json.load(f)

has_cell = False
for cell in nb['cells']:
    if cell['cell_type'] == 'markdown' and '## Step 6: Model Evaluation' in ''.join(cell['source']):
        has_cell = True
        break

if not has_cell:
    new_markdown = {
       "cell_type": "markdown",
       "metadata": {},
       "source": [
        "## Step 6: Model Evaluation\n",
        "The model is trained! Now we evaluate how good it actually is by generating predictions on our hidden `X_test` data and comparing them to the true `y_test` answers."
       ]
    }
    
    new_code = {
       "cell_type": "code",
       "execution_count": None,
       "metadata": {},
       "outputs": [],
       "source": [
        "from sklearn.metrics import mean_absolute_error, r2_score\n",
        "\n",
        "print(\"Generating predictions on the unseen test set...\")\n",
        "y_pred = rf_model.predict(X_test)\n",
        "\n",
        "# Calculate metrics\n",
        "mae = mean_absolute_error(y_test, y_pred)\n",
        "r2 = r2_score(y_test, y_pred)\n",
        "\n",
        "print(\"-\" * 40)\n",
        "print(\"MODEL EVALUATION METRICS\")\n",
        "print(\"-\" * 40)\n",
        "\n",
        "print(f\"Mean Absolute Error (MAE): {mae:.2f} ranks\")\n",
        "print(f\"R-squared (R²): {r2:.4f}\")\n",
        "\n",
        "# EXPLANATION OF R-SQUARED:\n",
        "# R^2 = 1.0 means the model perfectly predicts the closing rank every single time with zero errors.\n",
        "# R^2 = 0.5 means the model only explains 50% of the variance in the ranks (it's only halfway better than just guessing the historical average).\n",
        "# Since we included 'Opening Rank' as a feature, our R^2 should be exceptionally high!"
       ]
    }
    
    while nb['cells'] and nb['cells'][-1]['source'] == []:
        nb['cells'].pop()
        
    nb['cells'].extend([new_markdown, new_code])
    
    with open(path, "w") as f:
        json.dump(nb, f, indent=1)
    print("Successfully appended evaluation cells.")
else:
    print("Cells already exist.")
