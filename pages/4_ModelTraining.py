# Import necessary libraries
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
import joblib
from keras.models import Sequential
from keras.layers import Dense, SimpleRNN, Dropout
from trading.utils import *
from trading.trader import *
from trading.traditional_strategies import *
from trading.ai_strategies import *
from trading.rl_module import *
import warnings
warnings.filterwarnings("ignore")

# Streamlit page configuration
st.set_page_config(page_title="Model Training Page", page_icon="💡")

# Page title
st.title("AI Model Training Page")

# Stock selection
available_stocks = [
    "AAPL", "MSFT", "NVDA", "GOOG", "AMZN", "META",
    "BRK-B", "LLY", "AVGO", "TSLA", "WMT", "JPM", 
    "V", "UNH", "XOM", "ORCL", "MA", "HD", "PG", 
    "COST", "^SPX"
]

stock_ticker = st.selectbox("Select Training Stock Data", available_stocks)

# Date range for training data
min_date = datetime(2014, 1, 1)
max_date = datetime(2024, 10, 31)
start_date = st.date_input("Training Data Start Date", datetime(2014, 1, 1), min_value=min_date, max_value=max_date)
end_date = st.date_input("Training Data End Date", datetime(2024, 10, 31), min_value=min_date, max_value=max_date)

# Model selection
available_models = ["Logistic Regression", "RNN", "DQN"]
selected_model = st.selectbox("Select Training Model", available_models)



# Button to start training
if st.button("Start training"):
    # Placeholder for training status
    training_status = st.empty()

    # Load data
    data = pd.read_csv(f"./data/us_stock/all_{stock_ticker}.csv", parse_dates=["Date"], index_col="Date")
    data = data.loc[start_date:end_date]

    if selected_model in ["Logistic Regression",]:
        progress_bar = st.progress(0)  # Initialize progress bar
        status_text = st.empty()  # Placeholder for status updates

        # Step 1: Feature Engineering
        try:
            status_text.text("Calculating indicators and creating features...")
            data = calculate_indicators_df(data)
            progress_bar.progress(20)  # Update progress to 20%

            data['Target'] = (data['Close'].shift(-1) > data['Close']).astype(int)
            selected_features = ['Close', 'SMA_10', 'SMA_50', 'Momentum', 'RSI', 'MACD', 'BB_Middle', 'BB_Upper', 'BB_Lower']
            X = data[selected_features]
            y = data['Target']

            # Step 2: Scale Features
            status_text.text("Scaling features...")
            scaler = StandardScaler()
            X = scaler.fit_transform(X)
            scaler_file_path = f"./model/{stock_ticker}_scaler.pkl"
            joblib.dump(scaler, scaler_file_path)
            progress_bar.progress(50)  # Update progress to 50%

            # Step 3: Train Model
            status_text.text(f"Training {selected_model} model...")
            if selected_model == "Logistic Regression":
                model = LogisticRegression()
            elif selected_model == "Gradient Boosting":
                model = GradientBoostingClassifier()

            model.fit(X, y)
            progress_bar.progress(80)  # Update progress to 80%

            # Step 4: Save Model
            status_text.text(f"Saving {selected_model} model...")
            model_file_path = f"./model/{stock_ticker}_{selected_model.replace(' ', '_')}_model.pkl"
            joblib.dump(model, model_file_path)
            progress_bar.progress(100)  # Update progress to 100%

            # Completion
            progress_bar.empty()
            status_text.text("")
            training_status.success(f"{selected_model} model trained and saved for {stock_ticker}!")

        except Exception as e:
            progress_bar.empty()
            st.error(f"An error occurred: {e}")


    # Training RNN model
    elif selected_model == "RNN":
        # Function to prepare the dataset for RNN
        def prepare_dataset(data: pd.DataFrame, time_step: int = 50):
            """
            Prepare dataset for testing using the whole data.

            Args:
                data (pd.DataFrame): Stock data with 'Open' column.
                time_step (int): Number of timesteps for input sequences.

            Returns:
                X_data, scaler: Prepared input data and scaler.
            """
            dataset = data['Open'].values.reshape(-1, 1)
            scaler = MinMaxScaler(feature_range=(0, 1))
            dataset_scaled = scaler.fit_transform(dataset)

            # Prepare the entire dataset for testing
            X_data = []
            for i in range(time_step, len(dataset_scaled)):
                X_data.append(dataset_scaled[i - time_step:i, 0])

            # Convert to array
            X_data = np.array(X_data)

            # Reshape for RNN input
            X_data = np.reshape(X_data, (X_data.shape[0], X_data.shape[1], 1))

            return X_data, scaler

        # Function to build the RNN model
        def build_rnn(input_shape):
            """
            Build an RNN model.

            Args:
                input_shape (tuple): Shape of the input data.

            Returns:
                model: Compiled RNN model.
            """
            model = Sequential()
            model.add(SimpleRNN(units=50, activation="tanh", return_sequences=True, input_shape=input_shape))
            model.add(Dropout(0.2))
            model.add(SimpleRNN(units=50, activation="tanh", return_sequences=True))
            model.add(Dropout(0.2))
            model.add(SimpleRNN(units=50, activation="tanh", return_sequences=True))
            model.add(Dropout(0.2))
            model.add(SimpleRNN(units=50, activation="tanh", return_sequences=True))
            model.add(Dropout(0.2))
            model.add(SimpleRNN(units=50, activation="tanh", return_sequences=True))
            model.add(Dropout(0.2))
            model.add(SimpleRNN(units=50))
            model.add(Dropout(0.2))
            model.add(Dense(units=1))

            model.compile(optimizer="adam", loss="mean_squared_error")
            return model

        # Function to train the RNN model
        def train_rnn(model, X_train, y_train, epochs=50, batch_size=32):
            """
            Train the RNN model.

            Args:
                model: RNN model.
                X_train: Training input data.
                y_train: Training target data.
                epochs (int): Number of epochs.
                batch_size (int): Batch size.

            Returns:
                history: Training history.
            """
            progress_bar = st.progress(0)  # Initialize progress bar
            status_text = st.empty()  # Placeholder for status text
            total_steps = epochs

            for epoch in range(epochs):
                history = model.fit(X_train, y_train, epochs=1, batch_size=batch_size, verbose=0)
                current_loss = history.history['loss'][-1]
                
                # Update progress bar and status text
                progress_bar.progress((epoch + 1) / total_steps)
                status_text.text(f"Epoch {epoch + 1}/{epochs}, Loss: {current_loss:.4f}")
            
            progress_bar.empty()  # Clear progress bar
            status_text.text("Training Complete!")  # Final status
            return history


        # Function to make predictions
        def predict_rnn(model, X_data, scaler):
            """
            Make predictions using the trained RNN model.

            Args:
                model: Trained RNN model.
                X_data: Input data for predictions.
                scaler: Fitted MinMaxScaler.

            Returns:
                predictions: Predicted values (scaled back to original range).
            """
            predictions = model.predict(X_data)
            predictions = scaler.inverse_transform(predictions)
            return predictions
        
        try:
            training_status.info("Training started...")
            # Prepare the dataset
            time_step = 50
            X_data, scaler = prepare_dataset(data, time_step)

            # Build the RNN model
            rnn_model = build_rnn((X_data.shape[1], 1))

            # Train the model on the entire dataset
            X_train = X_data[:-1]
            y_train = data['Open'].values[time_step:len(data) - 1].reshape(-1, 1)
            y_train = scaler.fit_transform(y_train)  # Scale target values
            train_rnn(rnn_model, X_train, y_train)

            # Make predictions on the entire dataset
            predictions = predict_rnn(rnn_model, X_data, scaler)

            # Add predictions to the dataset
            data['predictions'] = np.nan
            data.iloc[time_step:, data.columns.get_loc('predictions')] = predictions.flatten()
            data.to_csv(f"./data/us_stock/predictions/{stock_ticker}.csv")
            training_status.success(f"RNN model trained and saved for {stock_ticker}!")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    
    # Training DQN model
    elif selected_model == "DQN":
        def train_dqn(stock_ticker):
            data = pd.read_csv(f"./data/us_stock/all_{stock_ticker}.csv")
            data['Date'] = pd.to_datetime(data['Date'])
            data.set_index('Date', inplace=True)

            # Initialize trading environment
            env = TradingEnv(data)
            state_size = env.observation_space.shape[0]
            action_size = env.action_space.n

            # Initialize DQN agent
            agent = DQNAgent(state_size, action_size)

            # Parameters for training
            episodes = 200
            batch_size = 32

            # Initialize Streamlit progress bar and status
            progress_bar = st.progress(0)  # Progress bar
            status_text = st.empty()  # Placeholder for status updates
            total_steps = episodes

            for e in range(episodes):
                state = env.reset()
                total_reward = 0

                for time in range(env.max_steps):
                    action = agent.act(state)
                    next_state, reward, done, _ = env.step(action)
                    agent.remember(state, action, reward, next_state, done)
                    state = next_state
                    total_reward += reward

                    if done:
                        break

                # Replay experiences and update the model
                agent.replay(batch_size)

                # Update progress bar and status text
                progress = (e + 1) / total_steps
                progress_bar.progress(progress)
                status_text.text(f"Episode {e + 1}/{episodes}, Total Reward: {total_reward}")

            # Save the trained model
            model_file_path = f"./model/{stock_ticker}_DQN_model.pth"
            torch.save(agent.model.state_dict(), model_file_path)
            status_text.text("")  # Clear status text
            progress_bar.empty()  # Clear progress bar

        try:
            # Start training
            training_status.info("DQN training started...")
            train_dqn(stock_ticker)
            training_status.success(f"DQN model trained and saved for {stock_ticker}!")
        except Exception as e:
            st.error(f"An error occurred: {e}")
