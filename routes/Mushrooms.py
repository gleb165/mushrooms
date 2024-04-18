from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form,Depends
from typing import Annotated
from models.Mushrooms import Mushroom, MushroomUpdate
from models.Users import User
from beanie import PydanticObjectId
from database.connection import Database
import io
import torch.nn as nn
import torch
from torchvision import models, transforms
from auth.authenticate import get_current_user
from PIL import Image



mushrooms_router = APIRouter(tags=["Mushroom"])
mushrooms_database = Database(Mushroom)


class ToRGB(object):
    def __call__(self, pic):
        if pic.mode != 'RGB':
            pic = pic.convert('RGB')
        return pic

@mushrooms_router.get("/", response_model=list[Mushroom])
async def retrieve_all_mushroom() -> list[Mushroom]:
    return await mushrooms_database.get_all()


@mushrooms_router.get("/mushroom", response_model=list[Mushroom])
async def retrieve_user_mushroom(current_user: Annotated[User, Depends(get_current_user)]) -> list[Mushroom]:
    mushroom = await Mushroom.find({'creator': current_user.email}).to_list()
    if not mushroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="mushroom with supplied ID does not exist"
        )
    return mushroom
@mushrooms_router.get('/mushroom_by_name', response_model=list[Mushroom])
async def retrieve_mushrooms_by_name(name: str) -> list[Mushroom]:
    mush = await mushrooms_database.get_mushroom_by_data(name)
    if not mush:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="mushroom with supplied ID does not exist"
        )
    return mush

@mushrooms_router.get("/{id}", response_model=Mushroom)
async def retrieve_one_mushroom(id: PydanticObjectId) -> Mushroom:
    mushroom = await mushrooms_database.get(id)
    if not mushroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="mushroom with supplied ID does not exist"
        )
    return mushroom
@mushrooms_router.post('/')
async def create_mushroom(current_user: Annotated[User, Depends(get_current_user)], name: str = Form(...),
                          price: int = Form(...), description: str = Form(...), image: UploadFile = File(...)):


    contents = await image.read()
    pil_image = Image.open(io.BytesIO(contents))

    # Load the saved model
    model = models.resnet18(pretrained=True)
    model.fc = nn.Linear(model.fc.in_features, 1000)  # Adjust to match the original model's output units
    model.load_state_dict(torch.load('model2good'))
    model.eval()

    # Create a new model with the correct final layer
    new_model = models.resnet18(pretrained=True)
    new_model.fc = nn.Linear(new_model.fc.in_features, 2)  # Adjust to match the desired output units

    # Copy the weights and biases from the loaded model to the new model
    new_model.fc.weight.data = model.fc.weight.data[0:2]  # Copy only the first 2 output units
    new_model.fc.bias.data = model.fc.bias.data[0:2]
    # Load and preprocess the unseen image
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        ToRGB(),  # Custom transform to convert PNG images to RGB
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    input_tensor = preprocess(pil_image)
    input_batch = input_tensor.unsqueeze(0)
    # Perform inference
    with torch.no_grad():
        output = model(input_batch)

    # Get the predicted class
    _, predicted_class = output.max(1)
    predict = bool(predicted_class)
    if predict is False:
        body = Mushroom(
            creator=current_user.email,
            name=name,
            price=price,
            predict=predict,
            description=description,  # Assuming no description available
            image=image.filename,
        )
        await mushrooms_database.save(body)
        return {'message': 'your mushrooms correct create'}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="mushroom is poison")


@mushrooms_router.put('/{id}', response_model=Mushroom)
async def update_mushroom(current_user: Annotated[User, Depends(get_current_user)], body: MushroomUpdate,
                          id: PydanticObjectId) -> Mushroom:
    mush = await mushrooms_database.get(id)
    if mush.creator != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operation not allowed"
        )
    update = await mushrooms_database.update(id, body)
    if not update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="mushroom with supplied ID does not exist"
        )
    return update


@mushrooms_router.delete('/{id}')
async def delete_mushroom(current_user: Annotated[User, Depends(get_current_user)], id: PydanticObjectId) -> dict:
    mush = await mushrooms_database.get(id)
    if mush.creator != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operation not allowed"
        )
    delete = await mushrooms_database.delete(id)
    if delete:
        return {'message': 'your mushrooms correct delete'}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="mushroom with supplied ID does not exist")

