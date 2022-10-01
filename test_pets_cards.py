import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.fixture(autouse=True)
def setup():
    pytest.driver = webdriver.Chrome(service=Service('C:/webdriver/chromedriver.exe'))
    pytest.driver.get('http://petfriends.skillfactory.ru/login')
    pytest.driver.find_element('id', 'email').send_keys('42@mail.com')
    pytest.driver.find_element('id', 'pass').send_keys('12345')
    pytest.driver.find_element('css selector', 'button[type="submit"]').click()
    yield
    pytest.driver.quit()


def test_all_pets():
    assert pytest.driver.find_element('tag name', 'h1').text == "PetFriends"
    # явное ожидание элементов 5 секунд
    images = WebDriverWait(pytest.driver, 5).until(EC.presence_of_all_elements_located(('class name', 'card-img-top')))
    names = WebDriverWait(pytest.driver, 5).until(EC.presence_of_all_elements_located(('class name', 'card-title')))
    description = WebDriverWait(pytest.driver, 5).until(EC.presence_of_all_elements_located
                                                        (('class name', 'card-text')))

    for i in range(len(names)):
        # Проверяем, что в каждой карточке есть атрибут scr в теге img
        assert images[i].get_attribute('src') is not None, f'Invalid structure of tag img, pet {names[i]} '
        assert names[i].text != ''
        assert description[i].text != ''
        assert ', ' in description[i].text
        parts = description[i].text.split(", ")
        assert len(parts[0]) > 0
        assert len(parts[1]) > 0


def test_show_my_pets():
    pytest.driver.get('https://petfriends.skillfactory.ru/my_pets')

    # неявное ожидание 5 секунд
    pytest.driver.implicitly_wait(5)
    images = pytest.driver.find_elements("xpath", '//*[@id="all_my_pets"]/table/tbody/tr/th/img')
    names = pytest.driver.find_elements("xpath", '//*[@id="all_my_pets"]/table/tbody/tr/td[1]')
    type_of_animal = pytest.driver.find_elements("xpath", '//*[@id="all_my_pets"]/table/tbody/tr/td[2]')
    age = pytest.driver.find_elements("xpath", '//*[@id="all_my_pets"]/table/tbody/tr/td[2]')
    len_of_animals = pytest.driver.find_element("xpath", '/html/body/div[1]/div/div[1]').text

    # проверяем, что количество карточек питомцев на странице соответствует счетчику питомцев
    assert len(names) == int(len_of_animals.split()[2])

    # вводим переменные для хранения множества имен, а также счетчика животных без фото
    set_of_pet_names = set()
    counter_of_pet_without_photo = 0

    # Создадим отдельное множество для хранения кортежа имени животного, типа и возраста.
    # До этой проверки дойти не должно, т.к. проверка на уникальность имени сработает раньше. Но задание есть задание)
    set_of_pets = set()

    for i in range(len(names)):
        # проверка на наличие имени, типа, возраста у животного
        assert names[i].text != '', 'Pet without name'
        assert type_of_animal[i].text != '', 'Pet without type'
        assert age[i].text != '', 'Pet without age'

        # Проверка уникальности имени животного
        if names[i].text not in set_of_pet_names:
            set_of_pet_names.add(names[i].text)
        else:
            assert 0, f'Unique name error, Имя питомца "{names[i].text}" не уникально'

        # Проверка уникальности одновременно имени, типа и возраста животного (но до этого теста не дойдет, так как
        # одинаковое имя сломает предыдущий тест
        if (names[i].text, type_of_animal[i].text, age[i].text) not in set_of_pets:
            set_of_pets.add((names[i].text, type_of_animal[i].text, age[i].text))
        else:
            assert 0, f'Recurrent card of animal {names[i].text, type_of_animal[i].text, age[i].text}'

        # используем счетчик для подсчета карточек животных без фото
        if images[i].get_attribute('src') == '':
            counter_of_pet_without_photo += 1

    # поднимаем AssertionError если количество животных без фото больше половины от общего числа
    if counter_of_pet_without_photo > len(names) / 2:
        assert 0, 'Too much pets without photo'
