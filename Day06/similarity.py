import numpy as np

def cosine_similarity(vector1, vector2):
    """
    Calculate the cosine similarity between two vectors.

    Args:
        vector1 (list or np.ndarray): First vector.
        vector2 (list or np.ndarray): Second vector.

    Returns:
        float: Cosine similarity between the two vectors.
    """
    # Convert lists to numpy arrays if they are not already
    vector1 = np.array(vector1)
    vector2 = np.array(vector2)

    # Calculate the dot product and norms
    dot_product = np.dot(vector1, vector2)
    norm_vector1 = np.linalg.norm(vector1)
    norm_vector2 = np.linalg.norm(vector2)

    # Handle the case where either vector is zero
    if norm_vector1 == 0 or norm_vector2 == 0:
        return 0.0

    # Calculate cosine similarity
    similarity = dot_product / (norm_vector1 * norm_vector2)
    
    return similarity