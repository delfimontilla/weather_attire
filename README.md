# Attire recommendations based on the current weather and the forecast for the day

## Project Description

This project aims to provide attire recommendations by analyzing the current weather conditions and the forecast for the day. It helps users make informed decisions about what to wear based on the weather conditions.

## Features

- Retrieves the current weather information from a weather API.
- Retrieves the forecast for the day from the same weather API.
- Analyzes the weather data to determine appropriate attire recommendations using [Gemma](https://huggingface.co/google/gemma-2b-it).
- Displays the attire recommendations in an easy-to-understand format.

## Installation

To install and run this project, follow these steps:

1. Clone the repository: `git clone https://github.com/delfimontilla/weather_attire.git`
2. Navigate to the project directory: `cd weather_attire`
3. Install the dependencies: `poetry install`
4. Configure your Hugging Face token in a json file inside the `config` directory.
5. Get access to Gemma Models in `https://huggingface.co/google/gemma-2b-it`

## Usage

Run the webapp with `poetry run streamlit run src/dashboard.py`.
Once the application is running, you can access it through your web browser clicking on the Network URL provided. When asked, the application will display the current weather information and provide attire recommendations based on the weather conditions.

## Contributing

Contributions are welcome! If you would like to contribute to this project, please follow these guidelines:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes and commit them: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Submit a pull request.

## License

This project is licensed under the GPL-3.0 License. See the [LICENSE](LICENSE) file for more details.
