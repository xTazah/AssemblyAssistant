import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout, Embedding, LSTM, Bidirectional
from keras.utils import pad_sequences
from keras.preprocessing.text import Tokenizer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import os


dir_path = os.path.dirname(os.path.realpath(__file__))

# Load  data
with open(os.path.join(dir_path, 'forward.txt'), 'r') as f:
    forward_data = f.readlines()

with open(os.path.join(dir_path, 'backward.txt'), 'r') as f:
    backward_data = f.readlines()

#with open(os.path.join(dir_path, 'other.txt'), 'r') as f:
    other_data = f.readlines()

data = forward_data + backward_data + other_data
labels = ['forward']*len(forward_data) + ['backward']*len(backward_data) + ['other']*len(other_data)

tokenizer = Tokenizer()
tokenizer.fit_on_texts(data)
sequences = tokenizer.texts_to_sequences(data)

# pad the sequences-->same length:
max_length = max([len(seq) for seq in sequences])
padded_sequences = pad_sequences(sequences, maxlen=max_length, padding='post')

label_encoder = LabelEncoder()
label_encoder.fit(labels)
encoded_labels = label_encoder.transform(labels)


X_train, X_test, y_train, y_test = train_test_split(padded_sequences, encoded_labels, test_size=0.2, random_state=42)

model = Sequential()
model.add(Embedding(input_dim=len(tokenizer.word_index)+1, output_dim=128, input_length=max_length))
model.add(Bidirectional(LSTM(units=128)))
model.add(Dense(units=64, activation='relu'))
model.add(Dropout(rate=0.5))
model.add(Dense(3, activation='softmax'))
model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

#model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=10)
model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=10, batch_size=32)

model.save('SpeechModel.h5')

#inference
new_data = ['this has nothing to do with the rest','proceed to the next step', "go one step back","im finihsed","forward", "i don't know whats going on","The operator error caused a delay"]

new_sequences = tokenizer.texts_to_sequences(new_data)
new_padded_sequences = pad_sequences(new_sequences, maxlen=max_length, padding='post')

predictions = model.predict(new_padded_sequences)

predicted_labels = label_encoder.inverse_transform([int(round(pred[0])) for pred in predictions])
np.set_printoptions(suppress=True)
print(predictions)
print(predicted_labels)
