from sklearn.metrics import classification_report, confusion_matrix
import numpy as np

# Evaluate the model on test data
test_loss, test_accuracy = model.evaluate(X_test, y_test)

# Get model predictions
y_pred = model.predict(X_test)
y_pred_classes = (y_pred > 0.5).astype("int32")  # Convert probabilities to binary (0 or 1)

# Generate evaluation metrics
report = classification_report(y_test, y_pred_classes)
conf_matrix = confusion_matrix(y_test, y_pred_classes)

# Save results to a text file
with open("evaluation_results.txt", "w") as f:
    f.write(f"Test Loss: {test_loss}\n")
    f.write(f"Test Accuracy: {test_accuracy}\n\n")
    f.write("Classification Report:\n")
    f.write(report + "\n")
    f.write("Confusion Matrix:\n")
    f.write(np.array2string(conf_matrix))
