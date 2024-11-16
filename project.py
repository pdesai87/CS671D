# -*- coding: utf-8 -*-
"""Project_levels.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/11UrWwUjwDhnJRR1q92l7lVqnGPo91MTR
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, roc_auc_score, f1_score, classification_report
from sklearn.ensemble import RandomForestClassifier
from imblearn.ensemble import BalancedRandomForestClassifier

import shap
from sklearn.svm import SVC
from sklearn.inspection import permutation_importance

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

from sklearn.linear_model import LogisticRegression

from xgboost import XGBClassifier

from sklearn.pipeline import Pipeline
from sklearn.neural_network import MLPClassifier

from sklearn.preprocessing import MinMaxScaler

"""# 1.2 Data Description

## Initial Data Assessment
"""

# Load the data
file_path = 'Animal Data.csv'
animal_data = pd.read_csv(file_path)

print(animal_data.info())
print(animal_data.describe())
animal_data

# Define abr metrics columns
abr_metrics = animal_data.columns[4:]

"""## Exploratory Data Analysis (EDA)"""

# Histograms for each ABR metric
for col in abr_metrics:
    plt.figure(figsize=(6, 4))
    sns.histplot(animal_data[col], kde=True)
    plt.title(f'Distribution of {col}')
    plt.show()

# Box Plots by Group to identify group differences
for col in abr_metrics:
    plt.figure(figsize=(6, 4))
    sns.boxplot(x='Group', y=col, data=animal_data)
    plt.title(f'{col} by Group')
    plt.show()

# Pair Plot of selected features by Group (might be unnecessary)
sns.pairplot(animal_data, hue="Group", vars=abr_metrics[:10])
plt.show()

# Correlation Matrix for ABR Metrics
corr_matrix = animal_data[abr_metrics].corr()
plt.figure(figsize=(12, 10))
sns.heatmap(corr_matrix, cmap="coolwarm", center=0)
plt.title("Correlation Matrix for ABR Metrics")
plt.show()

"""## Handling Missing Data"""

# Check if missing values exist in the dataset
missing_values = animal_data.isnull().sum().sum()
print("Missing values before imputation:", missing_values)
missing_summary = animal_data.isnull().sum()
print("Missing values by column before imputation:\n", missing_summary)

# Calculate the mean for the current metric column within the specific group and level and impute missing values in the column for the specific group and level
groups = animal_data['Group'].unique()
levels = animal_data['Levels'].unique()
for column in abr_metrics:
    for group in groups:
        for level in levels:
            group_level_mean = animal_data[(animal_data['Group'] == group) & (animal_data['Levels'] == level)][column].mean()
            animal_data.loc[(animal_data['Group'] == group) & (animal_data['Levels'] == level) & (animal_data[column].isnull()), column] = group_level_mean

# Verify that no missing values remain in the dataset
missing_values_after_imputation = animal_data.isnull().sum().sum()
print("Remaining missing values after imputation:", missing_values_after_imputation)

"""## Feature Engineering"""

# # Creating difference metrics (T2 - T0) for each ABR metric
# t0_metrics = [col for col in abr_metrics if col.endswith("T0")]
# t2_metrics = [col.replace("T0", "T2") for col in t0_metrics]

# # Compute the difference (T2 - T0) and add these as new columns
# for t0, t2 in zip(t0_metrics, t2_metrics):
#     diff_column = t2.replace("T2", "_diff")
#     animal_data[diff_column] = animal_data[t2] - animal_data[t0]

# animal_data

"""## Normalization"""

scaler = StandardScaler()
animal_data[abr_metrics] = scaler.fit_transform(animal_data[abr_metrics])

animal_data

"""## Outlier Detection and Handling"""

# Define outliers as values beyond 3 standard deviations from the mean and replace outliers with the mean of the column
for column in abr_metrics:
    column_mean = animal_data[column].mean()
    column_std = animal_data[column].std()

    outliers = (animal_data[column] > column_mean + 3 * column_std) | (animal_data[column] < column_mean - 3 * column_std)
    animal_data.loc[outliers, column] = column_mean

animal_data

"""## Dimension Reduction (PCA)"""

animal_data_pca = animal_data.copy(deep=True)

pca = PCA(n_components=2)
abr_pca = pca.fit_transform(animal_data_pca[abr_metrics])
animal_data_pca['PCA1'] = abr_pca[:, 0]
animal_data_pca['PCA2'] = abr_pca[:, 1]

plt.figure(figsize=(8, 6))
sns.scatterplot(data=animal_data_pca, x='PCA1', y='PCA2', hue='Group')
plt.title("PCA of ABR Metrics by Group")
plt.show()

animal_data

"""## Create subset of data"""

# Select only the T2 metrics (columns ending with 'T2') and the 'control' and '96 db' group
subset_data = animal_data[animal_data['Group'].isin(['control', '96db'])]

t2_columns = [col for col in subset_data.columns if col.endswith("T2")]
essential_columns = ['Group', 'Levels', 'SubjectID', 'Run']
subset_t2_data = subset_data[essential_columns + t2_columns]

subset_t2_data

"""## Separate features and target"""

# Split the data into training and testing sets
X = animal_data.drop(columns=['Group', 'SubjectID', 'Run'])
y = animal_data['Group']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Split the subset data into training and testing sets
X_subset = subset_t2_data.drop(columns=['Group', 'SubjectID', 'Run'])
y_subset = subset_t2_data['Group']

X_train_subset, X_test_subset, y_train_subset, y_test_subset = train_test_split(X_subset, y_subset, test_size=0.2, random_state=42, stratify=y_subset)

"""# 2

Certainly! I’ll include the specific evaluation metrics for each algorithm based on the previously discussed criteria. Here’s the final answer with evaluation metrics added for each model:

---

### 2 Methods

In this project, I selected algorithms that balance interpretability, computational efficiency, and the ability to handle high-dimensional, potentially non-linear relationships. The algorithms are implemented using high-quality libraries, such as **scikit-learn** and **XGBoost**, chosen for their reliability, robust optimization methods, and ease of use. Each model was trained using cross-validation to ensure robust performance and optimize hyperparameters effectively.

#### Algorithms, Training Procedures, and Evaluations

1. **Linear Discriminant Analysis (LDA)**:
   - **Motivation**: LDA is a strong choice for classification where interpretability and linear separation are prioritized. It provides clear insights into how different ABR metrics contribute to distinguishing noise-exposed groups.
   - **Training**: LDA works by computing the mean and pooled covariance of each class to find linear combinations of features (called discriminant functions) that maximize the separation between classes. The model seeks to maximize the between-class variance while minimizing the within-class variance, achieving optimal class separation. During training, LDA calculates a set of linear discriminants, each representing a direction that separates classes as much as possible. These discriminants are then used to classify new data points based on their projection onto these axes. To optimize performance, cross-validation is used to validate the model’s stability, ensuring it generalizes well to new data. The final LDA model provides interpretable coefficients, showing which combinations of ABR metrics most strongly differentiate noise exposure groups.
   - **Evaluation**: **Accuracy** is used to measure the overall classification performance. **Interpretability** is also emphasized, as LDA’s linear discriminants reveal how combinations of ABR metrics contribute to distinguishing groups. **F1 Score** helps balance performance in cases of class imbalance.

2. **Random Forest Classifier**:
   - **Motivation**: Random Forests are selected for their robustness in high-dimensional settings and ability to capture complex interactions between features. They also provide feature importance scores, aligning well with the project’s goal of identifying key ABR metrics.
   - **Training**: Random Forests are trained by constructing an ensemble of decision trees, each trained on a random subset of data and features. Each tree in the forest learns different patterns due to the randomness introduced, and the final classification for a data point is based on a majority vote across all trees. During training, trees are grown to a specified depth or until they meet certain criteria (e.g., minimum samples per leaf), and they use different feature splits at each node to minimize impurity (such as Gini impurity or entropy). The model’s robustness is enhanced through cross-validation, which helps determine the optimal number of trees, maximum depth, and other parameters to prevent overfitting. Feature importance scores are derived from the frequency and quality of feature splits across trees, helping to identify which ABR metrics are most predictive of noise exposure effects.
   - **Evaluation**: **Accuracy** is used as the primary metric, with **feature importance scores** providing insights into the ABR metrics that contribute most to classification. **ROC-AUC** is also calculated to assess the model’s ability to discriminate between classes, especially in binary comparisons (e.g., control vs. 96 dB). **F1 Score** is used to ensure balanced classification.

3. **Gradient Boosting Classifier (XGBoost)**:
   - **Motivation**: XGBoost is known for its high predictive performance and ability to capture subtle patterns, particularly in high-dimensional data with complex relationships. This makes it suitable for handling ABR metrics where non-linear relationships may exist.
   - **Training**: XGBoost is a boosting algorithm that iteratively builds decision trees, where each new tree corrects the residuals (errors) of the previous ones, thus improving accuracy with each iteration. It uses gradient descent to optimize a custom loss function (such as logistic loss for classification) and minimizes this loss with each step. During training, the model adjusts parameters such as the learning rate (step size for each iteration), maximum depth of trees, and number of boosting rounds. Cross-validation is used to fine-tune these hyperparameters, ensuring that the model avoids overfitting while maximizing predictive accuracy. XGBoost’s training process is highly efficient due to parallel processing, and it provides feature importance scores based on each feature’s contribution to reducing the model’s error, helping to identify impactful ABR metrics.
   - **Evaluation**: **Accuracy** is used to measure overall performance, while **feature importance** helps interpret the contribution of each ABR metric to model predictions. **ROC-AUC** is used to evaluate the model’s discrimination ability, and **F1 Score** provides a balanced performance measure, particularly useful if there is class imbalance.

4. **Logistic Regression (with regularization)**:
   - **Motivation**: Logistic Regression is chosen as a baseline for its interpretability and simplicity, which provides insights into the influence of each ABR metric on the likelihood of classifying data points correctly.
   - **Training**: Logistic Regression models the probability of a class as a logistic function of the linear combination of features, producing coefficients that represent the effect of each feature on the outcome. To prevent overfitting in high-dimensional settings, regularization (L1 or L2) is applied, shrinking less relevant coefficients towards zero, effectively performing feature selection. The regularization strength, represented by the hyperparameter C, controls the trade-off between maximizing likelihood and minimizing model complexity. Training involves maximizing the likelihood function using iterative optimization techniques like gradient descent, adjusting coefficients to best fit the data. Cross-validation is used to select the optimal regularization parameter, ensuring the model generalizes well without overfitting. The resulting model is interpretable, with coefficients indicating the influence of each ABR metric on classification, helping identify the most impactful features.
   - **Evaluation**: **Accuracy** measures overall model performance, while **interpretability** is achieved through the coefficients, which indicate each ABR metric’s influence on classification. **ROC-AUC** and **F1 Score** are also used to assess discrimination ability and balanced performance.

5. **Support Vector Machine (SVM) with RBF Kernel**:
   - **Motivation**: SVM with an RBF kernel is selected for its effectiveness in high-dimensional spaces and ability to handle non-linear separation, which may exist in the ABR data.
   - **Training**: SVM finds the optimal hyperplane that maximizes the margin between classes, and with the RBF kernel, it maps data into a higher-dimensional space to capture non-linear relationships. The training process involves optimizing a cost function that balances maximizing the margin and minimizing classification errors, controlled by the regularization parameter C. Additionally, the kernel parameter gamma determines the influence of individual data points on the decision boundary, with higher gamma values leading to tighter decision boundaries. Cross-validation is used to fine-tune C and gamma, ensuring the model achieves a good balance between accuracy and generalization. This process is computationally intensive, but the RBF kernel allows SVM to model complex patterns in the data that may not be linearly separable, improving classification performance for non-linear relationships.
   - **Evaluation**: **Accuracy** is used to assess overall performance. **ROC-AUC** measures the model’s ability to discriminate between classes, particularly for binary comparisons. **F1 Score** helps balance precision and recall, especially if there’s class imbalance.

6. **Partial Least Squares Discriminant Analysis (PLS-DA)**:
   - **Motivation**: PLS-DA is well-suited for high-dimensional, correlated data, like the ABR metrics, as it combines dimensionality reduction with classification by finding latent structures that differentiate classes.
   - **Training**: PLS-DA constructs latent components that maximize the covariance between predictors (ABR metrics) and the response variable (group classification). These components represent directions that capture the relationship between predictors and class separation, effectively reducing dimensionality while focusing on features that best discriminate between classes. The number of latent components is optimized through cross-validation to prevent overfitting and capture meaningful structures in the data. During training, the model iteratively refines these components to maximize their ability to separate classes, which provides insights into how ABR metrics relate to noise exposure groups. The resulting components help interpret which latent factors, composed of specific ABR metrics, are most relevant for distinguishing control and noise-exposed groups.
   - **Evaluation**: **Accuracy** measures overall performance, while **latent structures** offer interpretability by revealing relationships between ABR metrics and class labels. **F1 Score** is used to ensure balanced classification across groups, particularly in cases of class imbalance.

#### Summary of Evaluation Metrics
- **Accuracy**: Primary metric for each model to measure classification performance.
- **ROC-AUC Score**: Evaluates discrimination ability for binary comparisons.
- **F1 Score**: Balances precision and recall for cases with class imbalance.
- **Feature Importance and Interpretability**: Feature importance, coefficients, and latent structures help identify the most relevant ABR metrics.

This answer fully aligns with the project’s goals, covering motivations, training procedures, and evaluations comprehensively. Let me know if there’s anything further you need!

# 3.1

## Random Forest

### Entire Data
"""

model_results = {}

rf_params = {
    'n_estimators': [100, 200, 300],
    'max_depth': [10, 20, 30],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}
rf_grid = GridSearchCV(RandomForestClassifier(random_state=42), rf_params, cv=5, scoring='accuracy')
rf_grid.fit(X_train, y_train)

y_pred = rf_grid.predict(X_test)
model_results['Random Forest'] = {
    'Best Params': rf_grid.best_params_,
    'Accuracy': accuracy_score(y_test, y_pred),
    'ROC AUC': roc_auc_score(y_test, rf_grid.predict_proba(X_test), multi_class='ovr'),
    'F1 Score': f1_score(y_test, y_pred, average='weighted'),
    'Feature Importance': rf_grid.best_estimator_.feature_importances_,
    'Classification Report': classification_report(y_test, y_pred)
}

print("Random Forest (Entire Data) Results:")
print(model_results)

feature_importances_rf = rf_grid.best_estimator_.feature_importances_
feature_importance_df = pd.DataFrame({
    'Feature': X_test.columns,
    'Importance': feature_importances_rf
})

feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

plt.figure(figsize=(30, 26))
plt.barh(feature_importance_df['Feature'], feature_importance_df['Importance'], color='skyblue')
plt.gca().invert_yaxis()
plt.xlabel('Importance')
plt.title('Random Forest: Top ABR Metrics to Distinguish Control, 91db and 96 dB Groups')
plt.show()

"""### Subset"""

model_results_subset = {}

rf_params = {
    'n_estimators': [100, 200, 300],
    'max_depth': [10, 20, 30],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}
rf_grid_subset = GridSearchCV(RandomForestClassifier(random_state=42), rf_params, cv=5, scoring='accuracy')
rf_grid_subset.fit(X_train_subset, y_train_subset)

y_pred_subset = rf_grid_subset.predict(X_test_subset)
model_results_subset['Random Forest'] = {
    'Best Params': rf_grid_subset.best_params_,
    'Accuracy': accuracy_score(y_test_subset, y_pred_subset),
    'ROC AUC': roc_auc_score(y_test_subset, rf_grid_subset.predict_proba(X_test_subset)[:, 1]),
    'F1 Score': f1_score(y_test_subset, y_pred_subset, average='weighted'),
    'Feature Importance': rf_grid_subset.best_estimator_.feature_importances_,
    'Classification Report': classification_report(y_test_subset, y_pred_subset)
}

print("Random Forest (Subset Data) Results:")
print(model_results_subset)

feature_importances_rf_subset = rf_grid_subset.best_estimator_.feature_importances_
feature_importance_df = pd.DataFrame({
    'Feature': X_test_subset.columns,
    'Importance': feature_importances_rf_subset
})

feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

plt.figure(figsize=(20, 16))
plt.barh(feature_importance_df['Feature'], feature_importance_df['Importance'], color='skyblue')
plt.gca().invert_yaxis()
plt.xlabel('Importance')
plt.title('Random Forest: Top ABR Metrics to Distinguish Control and 96 dB Groups at T2')
plt.show()

"""## SVM

### Entire Data
"""

svm_params = {
    'C': [0.1, 1, 10],
    'gamma': ['scale', 'auto', 0.01, 0.1, 1]
}

svm_grid = GridSearchCV(SVC(kernel='rbf', probability=True, random_state=42), svm_params, cv=5, scoring='accuracy')
svm_grid.fit(X_train, y_train)


y_pred = svm_grid.predict(X_test)
model_results['SVM'] = {
    'Best Params': svm_grid.best_params_,
    'Accuracy': accuracy_score(y_test, y_pred),
    'ROC AUC': roc_auc_score(y_test, svm_grid.predict_proba(X_test), multi_class='ovr'),
    'F1 Score': f1_score(y_test, y_pred, average='weighted'),
    'Classification Report': classification_report(y_test, y_pred)
}

print("SVM (Entire Data) Results:")
print(model_results['SVM'])

# Calculate permutation importance
feature_importances = permutation_importance(svm_grid, X_test, y_test, scoring='accuracy', n_repeats=30, random_state=42)
feature_importances_svm = feature_importances.importances_mean
feature_importance_df = pd.DataFrame({
    'Feature': X_test.columns,
    'Importance': feature_importances_svm
})

feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

plt.figure(figsize=(30, 26))
plt.barh(feature_importance_df['Feature'], feature_importance_df['Importance'], color='skyblue')
plt.gca().invert_yaxis()
plt.xlabel('Importance')
plt.title('SVM: Top ABR Metrics to Distinguish Control, 91db and 96 dB Groups')
plt.show()

explainer = shap.KernelExplainer(svm_grid.best_estimator_.predict_proba, X_test.to_numpy())
shap_values = explainer.shap_values(X_test.to_numpy())

selected_class_shap_values = shap_values[:, :, 1]

shap_df = pd.DataFrame(selected_class_shap_values, columns=X_test.columns)
feature_importances_svm = shap_df.abs().mean(axis=0)

# Sort and visualize SHAP feature importances
feature_importance_df = pd.DataFrame({
    'Feature': X_test.columns,
    'Importance': feature_importances_svm
}).sort_values(by='Importance', ascending=False)

plt.figure(figsize=(30, 26))
plt.barh(feature_importance_df['Feature'], feature_importance_df['Importance'], color='skyblue')
plt.gca().invert_yaxis()
plt.xlabel('Importance')
plt.title('SVM: Top ABR Metrics to Distinguish Control, 91db and 96 dB Groups')
plt.show()

"""### Subset"""

svm_grid_subset = GridSearchCV(SVC(kernel='rbf', probability=True, random_state=42), svm_params, cv=5, scoring='accuracy')
svm_grid_subset.fit(X_train_subset, y_train_subset)

y_pred_subset = svm_grid_subset.predict(X_test_subset)
model_results_subset['SVM'] = {
    'Best Params': svm_grid_subset.best_params_,
    'Accuracy': accuracy_score(y_test_subset, y_pred_subset),
    'ROC AUC': roc_auc_score(y_test_subset, svm_grid_subset.predict_proba(X_test_subset)[:, 1]),
    'F1 Score': f1_score(y_test_subset, y_pred_subset, average='weighted'),
    'Classification Report': classification_report(y_test_subset, y_pred_subset)
}

print("SVM (Subset Data) Results:")
print(model_results_subset['SVM'])

feature_importances = permutation_importance(svm_grid_subset, X_test_subset, y_test_subset, scoring='accuracy', n_repeats=30, random_state=42)
feature_importances_svm_subset = feature_importances.importances_mean
feature_importance_df = pd.DataFrame({
    'Feature': X_test_subset.columns,
    'Importance': feature_importances_svm_subset
})

feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

plt.figure(figsize=(20, 16))
plt.barh(feature_importance_df['Feature'], feature_importance_df['Importance'], color='skyblue')
plt.gca().invert_yaxis()
plt.xlabel('Importance')
plt.title('SVM: Top ABR Metrics to Distinguish Control and 96 dB Groups at T2')
plt.show()

explainer = shap.KernelExplainer(svm_grid_subset.best_estimator_.predict_proba, X_test_subset.to_numpy())
shap_values = explainer.shap_values(X_test_subset.to_numpy())

selected_class_shap_values = shap_values[:, :, 1]

shap_df = pd.DataFrame(selected_class_shap_values, columns=X_test_subset.columns)
feature_importances_svm_subset = shap_df.abs().mean(axis=0)

feature_importance_df = pd.DataFrame({
    'Feature': X_test_subset.columns,
    'Importance': feature_importances_svm_subset
}).sort_values(by='Importance', ascending=False)

plt.figure(figsize=(30, 26))
plt.barh(feature_importance_df['Feature'], feature_importance_df['Importance'], color='skyblue')
plt.gca().invert_yaxis()
plt.xlabel('Importance')
plt.title('SVM: Top ABR Metrics to Distinguish Control, 91db and 96 dB Groups')
plt.show()

"""## LDA

### Entire Data
"""

lda_params = {
    'solver': ['svd', 'lsqr', 'eigen'],
    'shrinkage': [None, 'auto', 0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0],
}

lda_grid = GridSearchCV(LinearDiscriminantAnalysis(), lda_params, cv=5, scoring='accuracy', n_jobs=-1)
lda_grid.fit(X_train, y_train)

y_pred = lda_grid.predict(X_test)
model_results['LDA'] = {
    'Best Params': lda_grid.best_params_,
    'Accuracy': accuracy_score(y_test, y_pred),
    'ROC AUC': roc_auc_score(y_test, lda_grid.predict_proba(X_test), multi_class='ovr'),
    'F1 Score': f1_score(y_test, y_pred, average='weighted'),
    'Classification Report': classification_report(y_test, y_pred)
}

print("LDA (Entire Data) Results:")
print(model_results['LDA'])

feature_importances_lda = abs(lda_grid.best_estimator_.coef_[0])
feature_importance_df = pd.DataFrame({
    'Feature': X_test.columns,
    'Importance': feature_importances_lda
})

feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

plt.figure(figsize=(30, 26))
plt.barh(feature_importance_df['Feature'], feature_importance_df['Importance'], color='skyblue')
plt.gca().invert_yaxis()
plt.xlabel('Importance')
plt.title('LDA: Top ABR Metrics to Distinguish Control, 91db and 96 dB Groups')
plt.show()

"""### Subset"""

lda_params = {
    'solver': ['svd', 'lsqr', 'eigen'],
    'shrinkage': [None, 'auto', 0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0],
}

lda_grid_subset = GridSearchCV(LinearDiscriminantAnalysis(), lda_params, cv=5, scoring='accuracy', n_jobs=-1)
lda_grid_subset.fit(X_train_subset, y_train_subset)

y_pred_subset = lda_grid_subset.predict(X_test_subset)
model_results_subset['LDA'] = {
    'Best Params': lda_grid_subset.best_params_,
    'Accuracy': accuracy_score(y_test_subset, y_pred_subset),
    'ROC AUC': roc_auc_score(y_test_subset, lda_grid_subset.predict_proba(X_test_subset)[:, 1]),
    'F1 Score': f1_score(y_test_subset, y_pred_subset, average='weighted'),
    'Classification Report': classification_report(y_test_subset, y_pred_subset)
}

print("LDA (Subset Data) Results:")
print(model_results_subset['LDA'])

feature_importances_lda_subset = abs(lda_grid_subset.best_estimator_.coef_[0])
feature_importance_df = pd.DataFrame({
    'Feature': X_test_subset.columns,
    'Importance': feature_importances_lda_subset
})

feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

plt.figure(figsize=(20, 16))
plt.barh(feature_importance_df['Feature'], feature_importance_df['Importance'], color='skyblue')
plt.gca().invert_yaxis()
plt.xlabel('Importance')
plt.title('LDA: Top ABR Metrics to Distinguish Control and 96 dB Groups at T2')
plt.show()

"""## Logistic Regulation with Regularization

### Entire Dataset
"""

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score, roc_auc_score, f1_score, classification_report

logreg_params = {
    'penalty': ['l1', 'l2', 'elasticnet'],
    'C': [0.0001, 0.001, 0.01, 0.1, 1, 10, 100],
    'solver': ['liblinear', 'saga'],
    'l1_ratio': [0.1, 0.3, 0.5, 0.7, 0.9]
}

logreg_grid = GridSearchCV(LogisticRegression(max_iter=1000), logreg_params, cv=5, scoring='accuracy', n_jobs=-1)
logreg_grid.fit(X_train, y_train)

y_pred = logreg_grid.predict(X_test)
model_results['Logistic Regression'] = {
    'Best Params': logreg_grid.best_params_,
    'Accuracy': accuracy_score(y_test, y_pred),
    'ROC AUC': roc_auc_score(y_test, logreg_grid.predict_proba(X_test), multi_class='ovr'),
    'F1 Score': f1_score(y_test, y_pred, average='weighted'),
    'Classification Report': classification_report(y_test, y_pred)
}

print("Logistic Regression (Entire Data) Results:")
print(model_results['Logistic Regression'])

feature_importances_logreg = abs(logreg_grid.best_estimator_.coef_[0])
feature_importance_df = pd.DataFrame({
    'Feature': X_test.columns,
    'Importance': feature_importances_logreg
})

feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

plt.figure(figsize=(30, 26))
plt.barh(feature_importance_df['Feature'], feature_importance_df['Importance'], color='skyblue')
plt.gca().invert_yaxis()
plt.xlabel('Importance')
plt.title('Logistic Regression: Top ABR Metrics to Distinguish Control, 91db and 96 dB Groups')
plt.show()

"""### Subset"""

logreg_params = {
    'penalty': ['l1', 'l2', 'elasticnet'],
    'C': [0.0001, 0.001, 0.01, 0.1, 1, 10, 100],
    'solver': ['liblinear', 'saga'],
    'l1_ratio': [0.1, 0.3, 0.5, 0.7, 0.9]
}

logreg_grid_subset = GridSearchCV(LogisticRegression(max_iter=1000), logreg_params, cv=5, scoring='accuracy', n_jobs=-1)
logreg_grid_subset.fit(X_train_subset, y_train_subset)

y_pred_subset = logreg_grid_subset.predict(X_test_subset)
model_results_subset['Logistic Regression'] = {
    'Best Params': logreg_grid_subset.best_params_,
    'Accuracy': accuracy_score(y_test_subset, y_pred_subset),
    'ROC AUC': roc_auc_score(y_test_subset, logreg_grid_subset.predict_proba(X_test_subset)[:, 1]),
    'F1 Score': f1_score(y_test_subset, y_pred_subset, average='weighted'),
    'Classification Report': classification_report(y_test_subset, y_pred_subset)
}

print("Logistic Regression (Subset Data) Results:")
print(model_results_subset['Logistic Regression'])

feature_importances_logreg_subset = abs(logreg_grid_subset.best_estimator_.coef_[0])
feature_importance_df = pd.DataFrame({
    'Feature': X_test_subset.columns,
    'Importance': feature_importances_logreg_subset
})

feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

plt.figure(figsize=(20, 16))
plt.barh(feature_importance_df['Feature'], feature_importance_df['Importance'], color='skyblue')
plt.gca().invert_yaxis()
plt.xlabel('Importance')
plt.title('Logistic Regression: Top ABR Metrics to Distinguish Control and 96 dB Groups at T2')
plt.show()

"""## Neural Network

### Entire Dataset
"""

label_encoder = LabelEncoder()
y = label_encoder.fit_transform(animal_data['Group'])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

mlp_params = {
    'mlp__hidden_layer_sizes': [(50,), (100,), (100, 50)],
    'mlp__activation': ['relu', 'tanh'],
    'mlp__alpha': [0.0001, 0.001, 0.01],
    'mlp__learning_rate_init': [0.001, 0.01]
}

pipeline = Pipeline([
    ('mlp', MLPClassifier(max_iter=1000, random_state=42))
])

mlp_grid = GridSearchCV(estimator=pipeline, param_grid=mlp_params, cv=5, scoring='accuracy', n_jobs=-1)
mlp_grid.fit(X_train, y_train)

y_pred = mlp_grid.predict(X_test)
model_results['Neural Network'] = {
        'Best Params': mlp_grid.best_params_,
        'Accuracy': accuracy_score(y_test, y_pred),
        'ROC AUC': roc_auc_score(y_test, mlp_grid.predict_proba(X_test), multi_class='ovr'),
        'F1 Score': f1_score(y_test, y_pred, average='weighted'),
        'Classification Report': classification_report(y_test, y_pred)
}

print("MLP Classifier (Entire Data) Results:")
print(model_results['Neural Network'])

feature_importances = permutation_importance(mlp_grid.best_estimator_, X_test, y_test, n_repeats=10, random_state=42, n_jobs=-1)
feature_importances_mlp = feature_importances.importances_mean
feature_importance_df = pd.DataFrame({
    'Feature': X_test.columns,
    'Importance': feature_importances_mlp
})

feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

plt.figure(figsize=(30, 26))
plt.barh(feature_importance_df['Feature'], feature_importance_df['Importance'], color='skyblue')
plt.gca().invert_yaxis()
plt.xlabel('Importance')
plt.title('Neural Network: Top ABR Metrics to Distinguish Control, 91db and 96 dB Groups')
plt.show()

best_mlp_model = mlp_grid.best_estimator_.named_steps['mlp']
explainer = shap.KernelExplainer(best_mlp_model.predict, X_test, link="identity")

shap_values = explainer.shap_values(X_test)
shap_df = pd.DataFrame(shap_values, columns=X_test.columns)

feature_importances_mlp = np.abs(shap_df).mean(axis=0)

feature_importance_df = pd.DataFrame({
    'Feature': X_test.columns,
    'Importance': feature_importances_mlp
})

feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

plt.figure(figsize=(30, 26))
plt.barh(feature_importance_df['Feature'], feature_importance_df['Importance'], color='skyblue')
plt.gca().invert_yaxis()
plt.xlabel('Importance')
plt.title('Neural Network: Top ABR Metrics to Distinguish Control, 91db and 96 dB Groups by SHAP')
plt.show()

"""### Subset"""

label_encoder = LabelEncoder()
y_subset = label_encoder.fit_transform(subset_t2_data['Group'])

X_train_subset, X_test_subset, y_train_subset, y_test_subset = train_test_split(X_subset, y_subset, test_size=0.2, random_state=42, stratify=y_subset)

mlp_params = {
    'mlp__hidden_layer_sizes': [(50,), (100,), (100, 50)],
    'mlp__activation': ['relu', 'tanh'],
    'mlp__alpha': [0.0001, 0.001, 0.01],
    'mlp__learning_rate_init': [0.001, 0.01]
}

pipeline = Pipeline([
    ('mlp', MLPClassifier(max_iter=1000, random_state=42))
])

mlp_grid_subset = GridSearchCV(estimator=pipeline, param_grid=mlp_params, cv=5, scoring='accuracy', n_jobs=-1)
mlp_grid_subset.fit(X_train_subset, y_train_subset)

y_pred_subset = mlp_grid_subset.predict(X_test_subset)
model_results_subset['Neural Network'] = {
        'Best Params': mlp_grid.best_params_,
        'Accuracy': accuracy_score(y_test_subset, y_pred_subset),
        'ROC AUC': roc_auc_score(y_test_subset, mlp_grid_subset.predict_proba(X_test_subset)[:, 1]),
        'F1 Score': f1_score(y_test_subset, y_pred_subset, average='weighted'),
        'Classification Report': classification_report(y_test_subset, y_pred_subset)
}

print("MLP Classifier (Entire Data) Results:")
print(model_results_subset['Neural Network'])

feature_importances = permutation_importance(mlp_grid_subset.best_estimator_, X_test_subset, y_test_subset, n_repeats=10, random_state=42, n_jobs=-1)
feature_importance_df = pd.DataFrame({
    'Feature': X_test_subset.columns,
    'Importance': feature_importances.importances_mean
})

feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

plt.figure(figsize=(20, 16))
plt.barh(feature_importance_df['Feature'], feature_importance_df['Importance'], color='skyblue')
plt.gca().invert_yaxis()
plt.xlabel('Importance')
plt.title('Neural Network: Top ABR Metrics to Distinguish Control and 96 dB Groups at T2')
plt.show()

best_mlp_model = mlp_grid_subset.best_estimator_.named_steps['mlp']
explainer = shap.KernelExplainer(best_mlp_model.predict, X_test_subset, link="identity")

shap_values = explainer.shap_values(X_test_subset)
shap_df = pd.DataFrame(shap_values, columns=X_test_subset.columns)

feature_importances_mlp_subset = np.abs(shap_df).mean(axis=0)

feature_importance_df = pd.DataFrame({
    'Feature': X_test_subset.columns,
    'Importance': feature_importances_mlp_subset
})

feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

plt.figure(figsize=(20, 16))
plt.barh(feature_importance_df['Feature'], feature_importance_df['Importance'], color='skyblue')
plt.gca().invert_yaxis()
plt.xlabel('Importance')
plt.title('Neural Network: Top ABR Metrics to Distinguish Control and 96 dB Groups at T2 by SHAP')
plt.show()

"""## XGBoost

### Entire Dataset
"""

le = LabelEncoder()
X_train['Levels'] = le.fit_transform(X_train['Levels'])
X_test['Levels'] = le.transform(X_test['Levels'])

xgb_params = {
    'n_estimators': [50, 100, 200],
    'max_depth': [3, 5, 7],
    'learning_rate': [0.01, 0.1, 0.2],
}

xgb_grid = GridSearchCV(XGBClassifier(use_label_encoder=False, eval_metric='mlogloss'), xgb_params, cv=5, scoring='accuracy', n_jobs=-1)
xgb_grid.fit(X_train, y_train)

y_pred = xgb_grid.predict(X_test)
model_results['XGBoost'] = {
    'Best Params': xgb_grid.best_params_,
    'Accuracy': accuracy_score(y_test, y_pred),
    'ROC AUC': roc_auc_score(y_test, xgb_grid.predict_proba(X_test), multi_class='ovr'),
    'F1 Score': f1_score(y_test, y_pred, average='weighted'),
    'Classification Report': classification_report(y_test, y_pred)
}

print("XGBoost (Entire Data) Results:")
print(model_results['XGBoost'])

feature_importances_xgb = xgb_grid.best_estimator_.feature_importances_
feature_importance_df = pd.DataFrame({
    'Feature': X_test.columns,
    'Importance': feature_importances_xgb
})

feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

plt.figure(figsize=(30, 26))
plt.barh(feature_importance_df['Feature'], feature_importance_df['Importance'], color='skyblue')
plt.gca().invert_yaxis()
plt.xlabel('Importance')
plt.title('XGBoost: Top ABR Metrics to Distinguish Control, 91db and 96 dB Groups')
plt.show()

"""### Subset"""

le_subset = LabelEncoder()
X_train_subset['Levels'] = le_subset.fit_transform(X_train_subset['Levels'])
X_test_subset['Levels'] = le_subset.transform(X_test_subset['Levels'])

xgb_params = {
    'n_estimators': [50, 100, 200],
    'max_depth': [3, 5, 7],
    'learning_rate': [0.01, 0.1, 0.2],
}

xgb_grid_subset = GridSearchCV(XGBClassifier(use_label_encoder=False, eval_metric='mlogloss'), xgb_params, cv=5, scoring='accuracy', n_jobs=-1)
xgb_grid_subset.fit(X_train_subset, y_train_subset)

y_pred_subset = xgb_grid_subset.predict(X_test_subset)
model_results_subset['XGBoost'] = {
    'Best Params': xgb_grid_subset.best_params_,
    'Accuracy': accuracy_score(y_test_subset, y_pred_subset),
    'ROC AUC': roc_auc_score(y_test_subset, xgb_grid_subset.predict_proba(X_test_subset)[:, 1]),
    'F1 Score': f1_score(y_test_subset, y_pred_subset, average='weighted'),
    'Classification Report': classification_report(y_test_subset, y_pred_subset)
}

print("XGBoost (Subset Data) Results:")
print(model_results_subset['XGBoost'])

feature_importances_xgb_subset = xgb_grid_subset.best_estimator_.feature_importances_
feature_importance_df = pd.DataFrame({
    'Feature': X_test_subset.columns,
    'Importance': feature_importances_xgb_subset
})

feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

plt.figure(figsize=(20, 16))
plt.barh(feature_importance_df['Feature'], feature_importance_df['Importance'], color='skyblue')
plt.gca().invert_yaxis()
plt.xlabel('Importance')
plt.title('XGBoost: Top ABR Metrics to Distinguish Control and 96 dB Groups at T2')
plt.show()

"""# 3.4"""

importance_entire = {
    'Random Forest': feature_importances_rf,
    'SVM': feature_importances_svm,
    'LDA': feature_importances_lda,
    'Logistic Regression': feature_importances_logreg,
    'Neural Network': feature_importances_mlp,
    'XGBoost': feature_importances_xgb,
}

importance_df_entire = pd.DataFrame(importance_entire, index=X_test.columns)
importance_df_entire = importance_df_entire.sort_values(by='Random Forest', ascending=False)

scaler = MinMaxScaler()
importance_df_entire_scaled = pd.DataFrame(scaler.fit_transform(importance_df_entire),
                                           index=X_test.columns,
                                           columns=importance_df_entire.columns)

def create_heatmap(data, title):
    plt.figure(figsize=(10, 8))
    sns.heatmap(data, annot=False, cmap="Blues", fmt=".2f", cbar_kws={'label': 'Importance Score'})
    plt.title(title)
    plt.xlabel("Models")
    plt.ylabel("Features")
    plt.show()

create_heatmap(importance_df_entire_scaled, "Feature Importance Across Models with Complete Dataset and Levels Parameter")

importance_subset = {
    'Random Forest': feature_importances_rf_subset,
    'SVM': feature_importances_svm_subset,
    'LDA': feature_importances_lda_subset,
    'Logistic Regression': feature_importances_logreg_subset,
    'Neural Network': feature_importances_mlp_subset,
    'XGBoost': feature_importances_xgb_subset,
}

importance_df_subset = pd.DataFrame(importance_subset, index=X_test_subset.columns)
importance_df_subset = importance_df_subset.sort_values(by='Random Forest', ascending=False)

scaler = MinMaxScaler()
importance_df_subset_scaled = pd.DataFrame(scaler.fit_transform(importance_df_subset),
                                           index=X_test_subset.columns,
                                           columns=importance_df_entire.columns)

create_heatmap(importance_df_subset_scaled, "Variable Importance Across Models with Subset of Control vs 96db Groups at T2 and Levels Parameter")