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
df <- df[rowSums(is.na(df)) != ncol(df), ]



food_categories <- c(
  "Bakkerij", "Soepen, sauzen, kruiden, olie", "Diepvries", "Zuivel, eieren, boter",
  "Aardappel, groente, fruit", "Koffie, thee", "Ontbijtgranen en beleg", "Wijn en bubbels",
  "Vlees, vis", "Pasta, rijst en wereldkeuken", "Salades, pizza, maaltijden",
  "Snoep, chocolade, koek", "Chips, noten, toast, popcorn", "Kaas, vleeswaren, tapas",
  "Vegetarisch, vegan en plantaardig", "Tussendoortjes")

food_df <- df[df$Category_1 %in% food_categories, ]



df_on_sale <- subset(df, !is.na(Sale.price))[, 1:4]
df_on_sale$percent_discount <- 100 - floor((df_on_sale$Sale.price/df_on_sale$Regular.price)*100)