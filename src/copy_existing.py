import shutil
import os


shutil.copy2("./data_original/Ace_Bikes_Data.xlsx", "./data_full/Ace_Bikes_Data.xlsx")
shutil.copy2("./data_original/Data_Dictionary.xlsx", "./data_full/Data_Dictionary.xlsx")
shutil.copy2("./data_original/New_Categories.xlsx", "./data_full/New_Categories.xlsx")


shutil.copytree("./data_original/Reviews", "./data_full/Reviews")
shutil.copytree("./data_original/WebStats", "./data_full/WebStats")