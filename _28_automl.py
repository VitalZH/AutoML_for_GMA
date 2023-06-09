# -*- coding: utf-8 -*-
"""-28-automl.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/gist/VitalZH/1e492e54f524f2874a1de5f2b0db6dbd/-28-automl.ipynb

Существует несколько библиотек для автоматического машинного обучения (AutoML) в Keras. Некоторые из них:

*AutoKeras*: это библиотека AutoML, разработанная для Keras, которая автоматически определяет архитектуру нейронной сети и настраивает ее гиперпараметры. AutoKeras также предоставляет механизмы автоматического извлечения признаков и визуализации результатов.

*Keras Tuner*: это библиотека для настройки гиперпараметров моделей Keras. Keras Tuner предоставляет механизмы для выбора лучшей комбинации гиперпараметров, включая случайный поиск, поиск сетки и байесовский поиск.

*Talos*: это библиотека AutoML для Keras, которая использует байесовскую оптимизацию для выбора наилучших гиперпараметров модели. Talos также предоставляет механизмы автоматического создания отчетов и визуализации результатов.

*Hyperas*: это библиотека для автоматической настройки гиперпараметров Keras с использованием поиска по сетке. Hyperas позволяет определить границы для гиперпараметров, которые нужно настроить, и выполняет автоматическую настройку на основе заданной функции оценки.

Это не полный список, но эти библиотеки предоставляют множество возможностей для автоматической настройки моделей Keras.

# Подготовка и загрузка датасета с изображениями водителей
"""

# Commented out IPython magic to ensure Python compatibility.
import gdown                                     # Подключение модуля для загрузки данных из облака
import numpy as np                               # Библиотека работы с массивами
import matplotlib.pyplot as plt                  # Для отрисовки графиков
# %matplotlib inline
from PIL import Image                            # Для отрисовки изображений
import random as random                          # Генератор рандомных чисел
from sklearn.model_selection import train_test_split
from keras.optimizers import Adam                # Оптимизатор Adam
from tensorflow.keras.models import Sequential   # Сеть прямого распространения
from tensorflow.keras.layers import Dense, Conv2D, MaxPooling2D, Flatten, Dropout, BatchNormalization, GlobalAveragePooling2D, GlobalMaxPooling2D
from tensorflow.keras import utils               # Используем для to_categorical
from tensorflow.keras.preprocessing import image # Для отрисовки изображений
from google.colab import files                   # Для загрузки своей картинки
import os
import time
from tensorflow.keras.callbacks import EarlyStopping

# указываем количество категорий правильных ответов
category_count = 10
# Загрузка zip-архива с датасетом из облака на диск виртуальной машины colab
gdown.download('https://storage.yandexcloud.net/aiueducation/marketing/datasets/reality.zip', None, quiet=True)

# Разархивация датасета в директорию 'content/cars'
!unzip -qo "reality.zip" -d /content/reality

# Папка с папками картинок, рассортированных по категориям
IMAGE_PATH = '/content/reality/'

# Список с названиями категорий
os.listdir(IMAGE_PATH)

# Определение списка имен классов
CLASS_LIST = sorted(os.listdir(IMAGE_PATH))

# Определение количества классов
CLASS_COUNT = len(CLASS_LIST)

# Проверка результата
print(f'Количество классов: {CLASS_COUNT}, метки классов: {CLASS_LIST}')

data_files = []                           # Cписок путей к файлам картинок
data_labels = []                          # Список меток классов, соответствующих файлам

for class_label in range(CLASS_COUNT):    # Для всех классов по порядку номеров (их меток)
    class_name = CLASS_LIST[class_label]  # Выборка имени класса из списка имен
    class_path = IMAGE_PATH + class_name  # Формирование полного пути к папке с изображениями класса
    class_files = os.listdir(class_path)  # Получение списка имен файлов с изображениями текущего класса
    print(f'Размер класса {class_name} составляет {len(class_files)} изображений')

    # Добавление к общему списку всех файлов класса с добавлением родительского пути
    data_files += [f'{class_path}/{file_name}' for file_name in class_files]

    # Добавление к общему списку меток текущего класса - их ровно столько, сколько файлов в классе
    data_labels += [class_label] * len(class_files)

print('Общий размер базы для обучения:', len(data_labels))

IMG_WIDTH = 64                           # Ширина изображения
IMG_HEIGHT = 64                           # Высота изображения

data_images = []                          # Пустой список для данных изображений

for file_name in data_files:
    # Открытие и смена размера изображения
    img = Image.open(file_name).resize((IMG_WIDTH, IMG_HEIGHT)) 
    img_np = np.array(img)                # Перевод в numpy-массив
    data_images.append(img_np)            # Добавление изображения в виде numpy-массива к общему списку

x_data = np.array(data_images)            # Перевод общего списка изображений в numpy-массив
y_data = np.array(data_labels)            # Перевод общего списка меток класса в numpy-массив

print(f'В массив собрано {len(data_images)} фотографий следующей формы: {img_np.shape}')
print(f'Общий массив данных изображений следующей формы: {x_data.shape}')
print(f'Общий массив меток классов следующей формы: {y_data.shape}')

x_data.shape

# Нормированние массива изображений
x_data = x_data / 255.

# Делим данные на обучающую и проверочную выборки
x_train, x_val, y_train, y_val = train_test_split(x_data, y_data, test_size=0.05, random_state=42)

# Задаем batch_size
batch_size = 128

# Загружаем названия классов из набора данных по водителям:
classes=['drinking ', 'hair_and_makeup ', 'operating_the_radio ', 'reaching_behind ', 'safe_driving ', 'talking_on_the_phone_left  ', 'talking_on_the_phone_right  ', 'talking_to_passenger  ', 'texting_left  ', 'texting_right ']

# Превращаем выходы сетей в формат  one hot encoding
y_train = utils.to_categorical(y_train, category_count)

pic_shapes = x_train[0].shape
IMG_WIDTH = pic_shapes[0]
IMG_HEIGHT = pic_shapes[1]
num_channels = pic_shapes[2]

# Делаем решейп
x_train = x_train.reshape(x_train.shape[0], IMG_WIDTH, IMG_HEIGHT, num_channels)
x_val = x_val.reshape(x_val.shape[0],IMG_WIDTH, IMG_HEIGHT, num_channels)

y_val = utils.to_categorical(y_val, category_count)

print(x_train.shape)
print(x_val.shape)

print(y_train.shape)
print(y_val.shape)

"""# AutoKeras

Auto-Keras (AutoML for deep learning) - это библиотека, предоставляющая возможность автоматизировать процесс создания глубоких нейронных сетей без участия человека. Она позволяет быстро и эффективно находить лучшие гиперпараметры модели на основе различных алгоритмов оптимизации и случайного поиска. Библиотека AutoKeras была выпущена в 2018 году.

Библиотека может работать с изображениями, текстами и табличными данными.

Основная идея Auto-Keras заключается в том, чтобы автоматически находить наиболее эффективные архитектуры глубоких нейронных сетей на основе процесса обучения с подкреплением (reinforcement learning). В процессе работы Auto-Keras генерирует случайные архитектуры сетей и оценивает их производительность на основе метрик, заданных пользователем. Затем происходит отбор лучших моделей и дальнейшая оптимизация гиперпараметров, таких как количество слоев, их тип, количество нейронов в каждом слое, функции активации и т.д.

Auto-Keras использует набор примитивов, позволяющих генерировать различные архитектуры нейронных сетей, основанных на классических методах, таких как сверточные нейронные сети (Convolutional Neural Networks, CNN) и рекуррентные нейронные сети (Recurrent Neural Networks, RNN), а также на более современных методах, таких как ResNet и DenseNet. При этом процесс генерации новых моделей может занимать много времени и ресурсов.

Auto-Keras поддерживает использование как CPU, так и GPU, что позволяет быстрее обрабатывать большие объемы данных. Кроме того, библиотека предоставляет удобный интерфейс для интеграции с другими библиотеками, такими как Keras и TensorFlow, что позволяет использовать уже готовые модели и переносить результаты между различными проектами.

Параметры:

- **num_classes** Целое число (int). По умолчанию None. Если None, то оно будет получено из данных.
- **multi_label** bool: Булев тип. По умолчанию установлено значение False.
- **loss** Loss-функция Keras. По умолчанию используется 'binary_crossentropy' или 'categorical_crossentropy' в зависимости от количества классов.
- **metrics** Необязательный параметр, может принимать список метрик Keras, в виде строки, функции или экземпляра метрики, список списков метрик или словарь с именованными метриками. По умолчанию используется метрика 'accuracy'..
- **project_name** str: Строка. Название AutoModel. По умолчанию установлено значение 'image_classifier'.
- **max_trials** int: Целое число. Максимальное количество разных моделей Keras, которые будут протестированы. Поиск может завершиться до достижения максимального количества проб. По умолчанию равен 100.
- **directory** Optional[Union[str, pathlib.Path]]: Это строка. Путь к директории для сохранения результатов поиска. По умолчанию значение None, что создает папку с именем AutoModel в текущей директории.
- **objective** str: String. Название метрики модели для минимизации или максимизации, например, 'val_accuracy'. По умолчанию устанавливается 'val_loss'.
- **tuner** Optional[Union[str, Type[autokeras.engine.tuner.AutoTuner]]]: Строка или подкласс AutoTuner. Если строка, то должна быть одной из 'greedy', 'bayesian', 'hyperband' или 'random'. Она также может быть подклассом AutoTuner. Если не указано, то используется тюнер, специфичный для задачи, который сначала оценивает наиболее часто используемые модели для задачи, прежде чем исследовать другие модели.
- **overwrite** bool: Булевое значение. По умолчанию False. Если False, загружает существующий проект с тем же именем, если такой найден. В противном случае перезаписывает проект.
- **seed** Optional[int]: Это целочисленный параметр, который устанавливает случайное начальное значение для генератора случайных чисел, используемого во время обучения модели. Это позволяет воспроизводить результаты обучения на разных машинах и улучшает воспроизводимость результатов.
- **max_model_size** Целое число. Максимальное количество скалярных параметров в модели. Модели, размер которых превышает это значение, отбрасываются.
- **kwargs**: Этот параметр относится к конструктору AutoModel и позволяет указать любые аргументы, поддерживаемые этим классом. Класс AutoModel является базовым классом для всех поддерживаемых моделей в AutoKeras, таких как ImageClassifier, TextClassifier, StructuredDataClassifier, и другие. Конкретный список аргументов, поддерживаемых AutoModel, зависит от конкретного класса модели, который используется. В общем, аргументы могут включать в себя параметры для слоев, оптимизаторов, регуляризации и других компонентов модели.
"""

!pip install autokeras

import autokeras as ak

"""AutoKeras для многоклассовой классификации изображений на примере датасета с водителями

- Параметр *multi_label* отвечает за тип задачи мульти-лейбл классификации. Если multi_label=True, то задача считается мульти-лейбл классификацией, в которой каждый объект может иметь несколько меток (классов) из множества возможных меток. Если multi_label=False (по умолчанию), то каждый объект имеет только одну метку из возможных.
- *tuner* - алгоритм оптимизации (например, 'bayesian' или 'random');
 Он может принимать значения: 'greedy', 'bayesian', 'hyperband' или 'random'

**Эксперимент №1.**

max_trials=5

tuner='bayesian'
"""

# Обучение модели
# Определение EarlyStopping-коллбека
es_callback = EarlyStopping(monitor='val_loss', patience=4)
start_time = time.time()
clf = ak.ImageClassifier(overwrite=True, max_trials=5, num_classes=10, multi_label=False, loss="categorical_crossentropy", metrics=["accuracy"], 
                         project_name="my_project", directory="my_dir", seed=88, max_model_size=None, tuner='bayesian', objective ='val_accuracy')
# Обучаем 10  моделей
clf.fit(x_train, y_train, epochs=10, batch_size=64, callbacks=[es_callback])
end_time = time.time()
# Вывод времени обучения и точности модели
print("Total training time:", end_time - start_time)
print("Training accuracy:", clf.evaluate(x_train, y_train)[1])
print("Test accuracy:", clf.evaluate(x_val, y_val)[1])

# чтобы получить num_models лучших моделей:
best_models = clf.tuner.get_best_models(num_models=3)

best_models[0].summary()

best_models[1].summary()

best_models[2].summary()

# Предсказываем на основании лучшей модели на проверочной выборке
predicted_y = clf.predict(x_val)
print(predicted_y)

# Оцениваем лучшую модель с использованием тестовых данных.
print(clf.evaluate(x_val, y_val))

"""Аккураси получилась низкой, для лучших результатов нужно сделать больше запусков, поменяв параметр max_trials

**Эксперимент №2.**

max_trials=15

tuner='bayesian'

Запустим алгоритм на бОльшем количестве запусков и посмотрим, позволит ли это нам улучшить точность на проверочной выборке
"""

# Обучение модели
# Определение EarlyStopping-коллбека
es_callback = EarlyStopping(monitor='val_loss', patience=4)
start_time = time.time()
clf_2 = ak.ImageClassifier(overwrite=True, max_trials=15, num_classes=10, multi_label=False, loss="categorical_crossentropy", metrics=["accuracy"], 
                         project_name="my_project", directory="my_dir", seed=44, max_model_size=None, tuner='bayesian', objective ='val_accuracy')
# Обучаем 10  моделей
clf_2.fit(x_train, y_train, epochs=10, batch_size=64, callbacks=[es_callback], validation_data=(x_val, y_val))
end_time = time.time()
# Вывод времени обучения и точности модели
print("Total training time:", end_time - start_time)
print("Training accuracy:", clf_2.evaluate(x_train, y_train)[1])
print("Test accuracy:", clf_2.evaluate(x_val, y_val)[1])

"""Да, эксперимент удался, точность повысилась до 92% на проверочной выборке. Посмотрим на архитектуру лучшей модели:"""

model_2 = clf_2.export_model()
model_2.summary()

"""**Эксперимент №3.**

max_trials=25

tuner=None

В случае, когда тюнер не указывается, применяется тюнер 'greedy'

'Greedy' тюнер является наиболее простым тюнером и используется по умолчанию. Он рассматривает небольшой набор моделей, начиная с наиболее простой, и последовательно увеличивает их сложность. После каждого шага тюнер выбирает лучшую модель и продолжает увеличивать ее сложность, пока не достигнет максимально заданной глубины. Это означает, что тюнеру не нужно проводить вычислительно дорогостоящие эксперименты с очень сложными моделями, что делает его очень эффективным и быстрым. Однако, в связи с этим, 'greedy' тюнер может не сходиться к глобальному оптимуму и может пропустить более сложные модели, которые могут давать лучшее качество на данных.
"""

# Обучение модели
# Определение EarlyStopping-коллбека
es_callback = EarlyStopping(monitor='val_loss', patience=4)
start_time = time.time()
clf_3 = ak.ImageClassifier(overwrite=True, max_trials=25, num_classes=10, multi_label=False, loss="categorical_crossentropy", metrics=["accuracy"], 
                         project_name="my_project", directory="my_dir", seed=44, max_model_size=None, objective ='val_accuracy')
# Обучаем 10  моделей
clf_3.fit(x_train, y_train, epochs=10, batch_size=64, callbacks=[es_callback], validation_data=(x_val, y_val))
end_time = time.time()
# Вывод времени обучения и точности модели
print("Total training time:", end_time - start_time) 
print("Training accuracy:", clf_3.evaluate(x_train, y_train)[1])
print("Test accuracy:", clf_3.evaluate(x_val, y_val)[1])

model_3 = clf_3.export_model()
model_3.summary()

"""# AutoKeras для бинарной классификации текстов на основе датасета IMDB (Internet Movie Database) 

Это база данных, в которой хранится информация о фильмах, телешоу, актерах, кинокритиках и других связанных с кино сущностях. В рамках машинного обучения датасет IMDB относится к набору данных, содержащему рецензии на фильмы. Он содержит отзывы, оставленные пользователями сайта IMDB для фильмов в жанре «экшн» и «драма». Каждый отзыв помечен как положительный или отрицательный, и используется для задач классификации текста, например, для определения тональности текста.

В данном примере мы не будем указывать параметр tuner - таким образом используется настраиваемый для конкретной задачи tuner, который сначала оценивает наиболее часто используемые модели для задачи, а затем исследует другие модели.
"""

from sklearn.datasets import load_files
import tensorflow as tf
import autokeras as ak

# загружаем датасет с рецензиями для бинарной классификации текстов
dataset = tf.keras.utils.get_file(
    fname="aclImdb.tar.gz",
    origin="http://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz",
    extract=True,
)

# set path to dataset
IMDB_DATADIR = os.path.join(os.path.dirname(dataset), "aclImdb")

classes = ["pos", "neg"]
train_data = load_files(
    os.path.join(IMDB_DATADIR, "train"), shuffle=True, categories=classes
)
test_data = load_files(
    os.path.join(IMDB_DATADIR, "test"), shuffle=False, categories=classes
)

x_train = np.array(train_data.data)
y_train = np.array(train_data.target)
x_test = np.array(test_data.data)
y_test = np.array(test_data.target)

print(x_train.shape)  # (25000,)
print(y_train.shape)  # (25000, 1)
print(x_train[0][:50])  # this film was just brilliant casting

"""Важный момент - исли используется "тяжелая" предобученная модель, например, bert, AutoKeras сам уменьшает параметр batch_size, не прерывая обучение."""

# Запустим классификатор текстов, сделаем 5 моделей
clf = ak.TextClassifier(
    overwrite=True, max_trials=3, objective = 'val_accuracy'
)  
# Feed the text classifier with training data.
hist=clf.fit(x_train, y_train, epochs=10, validation_data=(x_test, y_test), batch_size=64)
# Predict with the best model.
predicted_y = clf.predict(x_test)
# Evaluate the best model with testing data.
print(clf.evaluate(x_test, y_test))

# Получаем лучшую модель
mod=clf.export_model()
mod.summary()

"""# Keras Tuner

Keras Tuner - это библиотека, которая помогает выбрать оптимальные гиперпараметры для моделей, созданных с помощью Keras. Это позволяет автоматизировать процесс оптимизации гиперпараметров, что может существенно сократить время и усилия, затраченные на поиск лучшей модели.

Keras Tuner обеспечивает удобный интерфейс для определения гиперпараметров, исследуемых во время поиска, а также для выбора стратегии поиска. Библиотека поддерживает несколько стратегий поиска гиперпараметров, включая случайный поиск, поиск по сетке и поиск по градиентам.

Основные компоненты Keras Tuner:

* HyperModel - класс, который определяет архитектуру модели, которую нужно настроить. Обычно он наследуется от класса keras.Model.
* HyperParameters - класс, который определяет гиперпараметры, которые необходимо настроить. Он содержит методы для определения типов гиперпараметров, их диапазонов значений и других характеристик.
* Tuner - класс, который определяет стратегию поиска гиперпараметров. Он принимает на вход объект HyperModel и HyperParameters, а затем настраивает гиперпараметры, используя выбранную стратегию поиска. Результатом работы Tuner является оптимальный набор гиперпараметров.
* Oracle - класс, который определяет правила остановки поиска. Он определяет, когда поиск должен быть остановлен на основе заданных условий, таких как количество итераций или улучшение метрики.
* Callbacks - классы обратного вызова, которые можно использовать для мониторинга и сохранения состояния поиска.

kerastuner.tuners - это модуль библиотеки Keras Tuner, который содержит различные классы тюнеров для поиска оптимальных гиперпараметров моделей Keras.

Тюнеры Keras Tuner позволяют оптимизировать гиперпараметры модели, выбирая наиболее перспективные варианты из заданного диапазона значений. В этом процессе тюнер автоматически обучает и оценивает модели с разными комбинациями гиперпараметров и выбирает лучшую на основе заданной метрики.

Классы тюнеров в kerastuner.tuners включают в себя:

- RandomSearch - ищет лучшие гиперпараметры, выбирая их случайным образом из заданного диапазона значений.
- Hyperband - комбинация методов градиентной оптимизации и оптимизации гиперпараметров. Этот тюнер использует алгоритм Hyperband для пропуска наиболее обещающих моделей и оптимизации гиперпараметров только для них.
- BayesianOptimization - использует байесовскую оптимизацию для поиска лучших гиперпараметров.
- Sklearn - тюнер для моделей, совместимых со Scikit-Learn. Он использует случайный поиск или генетические алгоритмы для оптимизации гиперпараметров.
"""

!pip install keras-tuner

from kerastuner.tuners import RandomSearch
from kerastuner.tuners import Hyperband
from kerastuner.engine.hyperparameters import HyperParameters
import keras_tuner as kt

# Определение функции для построения модели
def model_builder(hp):
  model = Sequential()
  #Настраиваем параметры  у первого слоя Conv2D
  #hp_units_dense = hp.Int('units', min_value=32, max_value=512, step=32)
  hp_units_conv2D = hp.Int('units', min_value=32, max_value=512, step=32)
  model.add(Conv2D(filters=hp_units_conv2D, kernel_size=3, activation='relu'))
  model.add(Flatten())
  model.add(Dense(10))

  # Настраиваем параметр learning rate для оптимайзера
  hp_learning_rate = hp.Choice('learning_rate', values=[1e-2, 1e-3, 1e-4])

  model.compile(optimizer=Adam(learning_rate=hp_learning_rate),
                loss='categorical_crossentropy',
                metrics=['accuracy'])

  return model

# Определение гиперпараметров для настройки
tuner_search = RandomSearch(model_builder,
                            objective='val_accuracy',
                            max_trials=10,
                            directory='output',
                            project_name='drivers_keras_tuner')

# Запуск настройки гиперпараметров
tuner_search.search(x_train, y_train, epochs=10, batch_size=64,  validation_data=(x_val, y_val))

# Получение наилучшей модели
best_model = tuner_search.get_best_models(num_models=1)[0]

# Оценка наилучшей модели на тестовых данных
test_loss, test_accuracy = best_model.evaluate(x_val, y_val)
print('Test accuracy:', test_accuracy)

best_model.summary()

"""Точность получилась очень низкой. Попробуем добавить слоев в модель, изменим Tuner на Hyperband"""

# Определение функции для построения модели
def model_builder_2(hp):
  model = Sequential()
  hp_units_dense = hp.Int('units', min_value=32, max_value=512, step=32)
  # Определение количества слоев и их размерности
  for i in range(hp.Int('num_layers', 1, 4)):
      model.add(Conv2D(filters=hp.Int('units_' + str(i), 32, 256, 32), kernel_size= 3, activation=hp.Choice('activation_' + str(i), ['relu', 'tanh', 'sigmoid'])))
  # Определение количества слоев и их размерности
  for i in range(hp.Int('num_layers', 1, 4)):
      model.add(Dense(units=hp.Int('units_' + str(i), 32, 256, 32), activation=hp.Choice('activation_' + str(i), ['relu', 'tanh', 'sigmoid'])))
  model.add(Flatten())
  model.add(Dense(10, activation="softmax"))
  hp_learning_rate = hp.Choice('learning_rate', values=[1e-3, 1e-4])

  model.compile(optimizer=Adam(learning_rate=hp_learning_rate),
                loss='categorical_crossentropy',
                metrics=['accuracy'])

  return model

# Определение гиперпараметров для настройки
tuner_search = Hyperband(model_builder_2,
                            objective='val_accuracy', max_epochs=15,
                            
                            directory='output',
                            project_name='drivers_keras_tuner_2')

# Запуск настройки гиперпараметров
tuner_search.search(x_train, y_train, epochs=7, batch_size=64,  validation_data=(x_val, y_val))

models = tuner_search.get_best_models(num_models=2)

best_model = tuner_search.get_best_models(num_models=1)[0]
best_model

# Получение наилучшей модели
best_model_2 = tuner_search.get_best_models(num_models=1)[0]

# Оценка наилучшей модели на тестовых данных
test_loss, test_accuracy_2 = best_model_2.evaluate(x_val, y_val)
print('Test accuracy:', test_accuracy_2)

best_model_2.summary()

"""KerasTuner включает несколько подклассов, называемых "tuners", которые определяют, какую стратегию использовать при поиске наилучших гиперпараметров. Некоторые из наиболее популярных тюнеров в KerasTuner включают GridSearch, RandomSearch и Hyperband.

RandomSearch выбирает случайную комбинацию гиперпараметров и проверяет ее. Hyperband - более эффективный тюнер, который использует несколько итераций и удаляет слабые модели, чтобы сосредоточиться на перспективных кандидатах.
Есть еще BayesianOptimization Tuner, Sklearn Tuner, The base Tuner class

После того как тюнер завершит процесс подбора наилучших гиперпараметров, он возвращает модель Keras, которая может быть использована для обучения на данных.

**Keras Tuner для бинарной классификации текстов**
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

from kerastuner.tuners import RandomSearch
from kerastuner.engine.hyperparameters import HyperParameters

# Загрузка данных
data = keras.datasets.imdb
(train_data, train_labels), (test_data, test_labels) = data.load_data(num_words=10000)

# Преобразование данных
train_data = keras.preprocessing.sequence.pad_sequences(train_data, value=0, padding='post', maxlen=256)
test_data = keras.preprocessing.sequence.pad_sequences(test_data, value=0, padding='post', maxlen=256)

# Определение функции для построения модели
def build_model(hp):
    model = keras.Sequential()
    # Добавление слоев эмбеддинга
    model.add(layers.Embedding(input_dim=10000, output_dim=hp.Int('embedding_dim', min_value=32, max_value=256, step=32)))
    model.add(layers.GlobalAveragePooling1D())
    # Определение количества слоев и их размерности
    for i in range(hp.Int('num_layers', 1, 4)):
        model.add(layers.Dense(units=hp.Int('units_' + str(i), 32, 256, 32), activation=hp.Choice('activation_' + str(i), ['relu', 'tanh', 'sigmoid'])))
    model.add(layers.Dense(1, activation='sigmoid'))

    # Определение оптимизатора и скомпилирование модели
    model.compile(optimizer=keras.optimizers.Adam(hp.Choice('learning_rate', [1e-2, 1e-3, 1e-4])),
                  loss=keras.losses.BinaryCrossentropy(from_logits=True),
                  metrics=['accuracy'])

    return model

# Определение гиперпараметров для настройки
tuner_search = RandomSearch(build_model,
                            objective='val_accuracy',
                            max_trials=5,
                            directory='output',
                            project_name='imdb_sentiment_analysis')

# Запуск настройки гиперпараметров
tuner_search.search(train_data, train_labels, epochs=5, validation_split=0.2)

# Получение наилучшей модели
best_model = tuner_search.get_best_models(num_models=1)[0]

# Оценка наилучшей модели на тестовых данных
test_loss, test_accuracy = best_model.evaluate(test_data, test_labels)
print('Test accuracy:', test_accuracy)

# Получение наилучшей модели
best_model_3 = tuner_search.get_best_models(num_models=1)[0]

best_model_3.summary()

"""Функция build_model определяет архитектуру модели с помощью Keras Tuner. Она принимает объект HyperParameters, который содержит гиперпараметры, которые мы хотим оптимизировать. В этом примере мы оптимизируем гиперпараметры, связанные с размерностью векторного пространства эмбеддингов, количеством слоев и их размерностью, функциями активации и скоростью обучения.

Мы используем класс RandomSearch из Keras Tuner для настройки гиперпараметров. Метод search запускает процесс настройки, в котором модели обучаются на обучающем наборе данных и проверяются на валидационном наборе данных для оценки их производительности. Мы указываем максимальное количество испытаний (max_trials), которые хотим выполнить, а также папку directory и имя проекта project_name, в которых будут храниться результаты настройки.

После того, как настройка завершена, мы получаем наилучшую модель с помощью метода get_best_models. Затем мы оцениваем производительность этой модели на тестовом наборе данных с помощью метода evaluate.

# Talos

Talos - это библиотека для автоматической настройки гиперпараметров моделей глубокого обучения. Talos основана на библиотеке Keras и предоставляет простой и удобный API для оптимизации гиперпараметров.

С помощью Talos вы можете оптимизировать различные гиперпараметры, такие как размер батча, скорость обучения, количество слоев и их размерность, функции активации, параметры регуляризации и многое другое. Talos использует методы оптимизации, такие как Grid Search, Random Search, Fmin и другие, чтобы найти наилучшую комбинацию гиперпараметров.

Основной функциональностью Talos является Scan(), которая запускает процесс поиска оптимальных гиперпараметров. Она принимает на вход модель, гиперпараметры, настройки оптимизации и данные для обучения. После этого она запускает обучение и проверку модели с различными комбинациями гиперпараметров и сохраняет результаты.
"""

!pip install talos

import talos as ta
from talos.model.normalizers import lr_normalizer
from talos import Scan
#from talos.utils import dataset

# Определяем модель
def talos_model(x_train, y_train, x_val, y_val, params):
    model = Sequential()
    model.add(Conv2D(params['filters'], kernel_size=3, activation=params['activation'], input_shape=(64, 64, 3)))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Conv2D(params['filters'], kernel_size=3, activation=params['activation']))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Flatten())
    model.add(Dense(params['hidden_units'], activation=params['activation']))
    model.add(Dropout(params['dropout']))
    model.add(Dense(10, activation='softmax'))

    # Компилируем модель
    model.compile(loss='categorical_crossentropy', optimizer=Adam(lr=params['learning_rate']), metrics=['accuracy'])

    # Обучаем модель
    history = model.fit(x_train, y_train,
                        validation_data=(x_val, y_val),
                        batch_size=params['batch_size'],
                        epochs=10,
                        verbose=0)
    return history, model

# Определяем гиперпараметры
p = {'filters': [16, 32],
     #'kernel_size': [(3, 3), (5, 5)],
     'hidden_units': [32, 64],
     'dropout': [0.2, 0.3],
     'batch_size': [32, 64],
     #'epochs': [5, 10],
     'activation': ['relu', 'elu'],
     'learning_rate': [0.001, 0.0001]}

# Запускаем оптимизацию гиперпараметров
scan_object = ta.Scan(x=x_train,
                      y=y_train,
                      x_val=x_val,
                      y_val=y_val,
                      model=talos_model,
                      params=p,
                      experiment_name='talos_mod')

# получаем отчет о результатах сканирования
r = ta.Reporting(scan_object)

# выводим лучшие параметры
print(r.best_params)

r.data

best_params = r.best_params(metric='val_accuracy', exclude=['param1', 'param2'])

best_params

"""# Auto-sklearn

Auto-sklearn - это библиотека автоматического машинного обучения на основе фреймворка scikit-learn. Она использует методики обучения на основе градиентного спуска и генетические алгоритмы для автоматического поиска лучших параметров модели. Auto-sklearn поддерживает как задачи классификации, так и задачи регрессии. Эта библиотека позволяет автоматически настраивать гиперпараметры и выбирать алгоритмы машинного обучения для данной задачи, что упрощает процесс обучения моделей и повышает их качество.

AutoSklearnClassifier является классификатором, основанным на автоматическом машинном обучении. Он использует методы оптимизации для автоматического подбора модели и гиперпараметров на основе заданной метрики качества.

Некоторые из важных параметров AutoSklearnClassifier:

- time_left_for_this_task: (int, default=3600) - ограничение времени, выделенное для автоматического поиска лучшей модели. Значение указывается в секундах.
- per_run_time_limit: (int, default=360) - максимальное время работы для одного вызова модели, выраженное в секундах.
- memory_limit: (int, default=3072) - ограничение памяти, которую может использовать модель в мегабайтах.
- ensemble_size: (int, default=50) - количество лучших моделей, выбранных для ансамблирования.
- resampling_strategy: (str, default='holdout') - стратегия для оценки качества моделей. Допустимые значения - holdout, cv, cv-10, cv-5x2, subsample, subsample-iterative-fit.
- metric: (str, default='accuracy') - метрика, используемая для оценки качества моделей. Допустимые значения - accuracy, balanced_accuracy, f1, roc_auc, precision, recall, log_loss.
- n_jobs: (int, default=1) - количество параллельных процессов для обучения моделей.
"""

!pip install auto-sklearn

"""**Пример использования библиотеки auto-sklearn на основе табличных данных (датасет breast_cancer)**"""

from pprint import pprint
import sklearn.datasets
import sklearn.metrics
import sklearn.model_selection

X, y = sklearn.datasets.load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = sklearn.model_selection.train_test_split(
    X, y, random_state=1
)

import autosklearn
from autosklearn import classification
cls = autosklearn.classification.AutoSklearnClassifier(
    time_left_for_this_task=120,
    per_run_time_limit=30,
    tmp_folder='/tmp/autosklearn_classification_example_tmp' 
)

cls.fit(X_train, y_train, dataset_name="breast_cancer")

print(cls.leaderboard())

pprint(cls.show_models(), indent=4)