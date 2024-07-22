library(stringr)

# Retrieve data from filepath
working_dir <- getwd()
project_root_dir <- file.path(dirname(working_dir))
data_file_path <- file.path(project_root_dir, "complete_datasets", "2024-07-07.csv")

# Load dataframe
df <- read.csv(data_file_path)

# Ensure numeric data type
df[, c(2, 3, 10:19)] <- sapply(df[, c(2, 3, 10:19)], as.numeric)

# Remove empty cases
#df <- df[rowSums(is.na(df)) != ncol(df), ]



food_categories <- c(
  "Bakkerij", "Soepen, sauzen, kruiden, olie", "Diepvries", "Zuivel, eieren, boter",
  "Aardappel, groente, fruit", "Koffie, thee", "Ontbijtgranen en beleg", "Wijn en bubbels",
  "Vlees, vis", "Pasta, rijst en wereldkeuken", "Salades, pizza, maaltijden",
  "Snoep, chocolade, koek", "Chips, noten, toast, popcorn", "Kaas, vleeswaren, tapas",
  "Vegetarisch, vegan en plantaardig", "Tussendoortjes")

food_df <- df[df$Category_1 %in% food_categories, ]



df_on_sale <- subset(df, !is.na(Sale.price))[, 1:4]
df_on_sale$percent_discount <- 100 - floor((df_on_sale$Sale.price/df_on_sale$Regular.price)*100)


# df of price change over time
price_change_df <- data.frame("Product" = df$Product)

dataset_list <- list.files(file.path(project_root_dir, "complete_datasets"))

for (file in dataset_list) {
  
  file_path <- file.path(project_root_dir, "complete_datasets", file)
  
  # Read the dataset
  temp_df <- read.csv(file_path)
  
  # Extract the date part from the file name (remove the .csv part)
  date_name <- sub(".csv$", "", file)
  
  price_change_df[[date_name]] <- temp_df$Regular.price
  
}

price_change_df <- price_change_df[apply(price_change_df[, -1], 1, function(row) any(diff(row) != 0, na.rm = TRUE)), ] 
price_change_df$Difference <- price_change_df[, ncol(price_change_df)] - price_change_df[, 2]