from torchvision import transforms


def preprocess_image(X):
    try:
        return transforms.ToTensor()(X).unsqueeze(0)
    except Exception as e:
        raise
