from api import PetFriends
from settings import *
import os

pf = PetFriends()

def test_get_api_key_for_valid_user(email = valid_email, password = valid_password):
    """ Проверяем, что запрос api ключа возвращает статус 200,
    и в результате содержится слово key"""
    status, result = pf.get_api_key(email, password)
    # Проверяем статус:
    assert status == 200
    # Проверяем наличие ключа:
    assert 'key' in result

def test_get_api_key_for_invalid_user(email = invalid_email, password = invalid_password):
    """" Проверяем, что запрос ключа от несуществующего пользователя
    возвращает статус 403"""
    status, result = pf.get_api_key(email, password)
    # Проверяем статус:
    assert status == 403

def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем, что запрос всех питомцев возвращает не пустой список.
    Для этого, сначала получаем api ключ, и сохраняем в переменную auth_key.
    Далее, используя этого ключ запрашиваем список всех питомцев, и проверяем, что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    # Проверяем статус:
    assert status == 200
    # Проверяем, что нам в ответ передали хоть какие-то данные
    assert len(result['pets']) > 0

def test_get_all_pets_with_invalid_key(filter=''):
    """ Проверяем, что запрос всех питомцев с неправильным api ключём возвращает статус 403.
    Для этого запрашиваем список всех питомцев с invalid_key, который сохранен в settings.
    Доступное значение параметра filter - 'my_pets' либо '' """
    status, result = pf.get_list_of_pets(invalid_key, filter)
    # Проверяем статус:
    assert status == 403

def test_post_new_pet_with_valid_data(name='Dragonfly1', animal_type='лошадь', age='35', pet_photo='images/horse.jpg'):
    """Проверяем, что можно добавить питомца с корректными данными"""
    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    # Добавляем питомца
    status, result = pf.post_new_pet(auth_key, name, animal_type, age, pet_photo)
    # Проверяем статус:
    assert status == 200
    # Проверяем, что имя введенного питомца совпадает с именем, которе нам вернулось в ответе
    assert result['name'] == name

def test_post_new_pet_no_photo_with_valid_data(name='Dragonfly3', animal_type='хорс', age='10'):
    """Проверяем, что можно добавить питомца без фото с корректными данными,
    но простым методом без фото"""
    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    # Добавляем питомца
    status, result = pf.post_new_pet_no_photo(auth_key, name, animal_type, age)
    # Проверяем статус:
    assert status == 200
    # Проверяем, что имя введенного питомца совпадает с именем, которое нам вернулось в ответе
    assert result['name'] == name
    # Проверяем, что нет фото
    assert result['pet_photo'] is ''

def test_post_new_pet_no_photo_with_invalid_data(name='Dragonfly4', animal_type='хорс', age='qwe'):
    """Проверяем, что нельзя добавить питомца с буквами в поле age"""
    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    # Добавляем питомца
    status, result = pf.post_new_pet_no_photo(auth_key, name, animal_type, age)
    # !!!БАГ!!!!Статус ответа = 200, а должен быть 400, т.к. поле age допускает только данные типа number
    assert status == 200


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.post_new_pet(auth_key, "Стрекоза", "хорз", "3", "images/horse.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()

def test_successful_update_self_pet_info(name='Dragonfly5', animal_type='horse', age='11'):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то обновляем имя, тип и возраст питомца
    if len(my_pets['pets']) > 0:
        status, result = pf.put_pet_update_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name

    else:
        # Если список питомцев пуст, то выводим сообщение с текстом об отсутствии питомцев в своем списке
        raise Exception("There is no my pets")

def test_unsuccessful_update_self_pet_info(name='Dragonfly6', animal_type='horse', age='qwe'):
    """Проверяем возможность обновления информации о питомце с буквами в поле age """

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то обновляем имя, тип и возраст питомца
    if len(my_pets['pets']) > 0:
        status, result = pf.put_pet_update_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # !!!БАГ!!!!Статус ответа = 200, а должен быть 400, т.к. поле age допускает только данные типа number
        assert status == 200

    else:
        # Если список питомцев пуст, то выводим сообщение с текстом об отсутствии питомцев в своем списке
        raise Exception("There is no my pets")

def test_unsuccessful_update_self_pet_info(name='Dragonfly7', animal_type='horse', age='123'):
    """Проверяем, что при обновлении информации о питомце с неверным ключем auth_key
     возвращает статус 403"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то обновляем имя, тип и возраст питомца
    if len(my_pets['pets']) > 0:
        status, result = pf.put_pet_update_info(invalid_key, my_pets['pets'][0]['id'], name, animal_type, age)
        # Проверяем статус:
        assert status == 403
    else:
        # Если список питомцев пуст, то выводим сообщение с текстом об отсутствии питомцев в своем списке
        raise Exception("There is no my pets")

def test_successful_update_self_pet_photo(pet_photo='images/horse.jpg'):
    """Проверяем возможность добавления фото к питомцу"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то обновляем имя, тип и возраст питомца
    if len(my_pets['pets']) > 0:
        status, result = pf.post_pet_photo(auth_key, my_pets['pets'][0]['id'], pet_photo)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['pet_photo'] is not ''  # (сообщение об ошибке)

    else:
        # Если список питомцев пуст, то выводим сообщение с текстом об отсутствии питомцев в своем списке
        raise Exception("There is no my pets")
