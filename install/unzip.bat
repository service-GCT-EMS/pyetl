FOR /F "tokens=* USEBACKQ" %%F IN (`dir /B *.zip`) DO (
SET var=%%F
)
cd ..\mapper
tar -xf ..\install\%var%
python mapper.py #autodoc