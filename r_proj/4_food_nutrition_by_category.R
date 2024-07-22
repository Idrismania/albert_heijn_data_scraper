library(ggplot2)

columns_to_check <- c("Energy..kcal.", "Carbohydrates", "Fats", "Protein")

nutrition_df <- food_df[complete.cases(food_df[, columns_to_check]), ]
rownames(nutrition_df) <- NULL
nutrition_df <- nutrition_df[c(-8799, -9839),]


# Create a violin plot for each category with adjusted width and scale
p_cal <- ggplot(nutrition_df, aes(x = reorder(Category_1, Energy..kcal., FUN = median), y = Energy..kcal.)) +
  geom_violin(trim = FALSE, scale = "width", fill = "black", alpha=0.5) +
  geom_boxplot(width=0.25, alpha=0.5)+
  labs(x = "", y = "Energy (kcal) per 100 grams or ml", title = "Distribution of Energy (kcal) by Category") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1),
        plot.title = element_text(hjust = 0.5)) +
  coord_flip()  # Flip coordinates for horizontal orientation


# Create a violin plot for each category with adjusted width and scale
p_carb <- ggplot(nutrition_df, aes(x = reorder(Category_1, Carbohydrates, FUN = median), y = Carbohydrates)) +
  geom_violin(trim = FALSE, scale = "width", fill = "black", alpha=0.5) +
  geom_boxplot(width=0.25, alpha=0.5)+
  labs(x = "", y = "Carbohydrates (g) per 100 grams or ml", title = "Distribution of Carbohydrates by Category") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1),
        plot.title = element_text(hjust = 0.5)) +
  coord_flip()  # Flip coordinates for horizontal orientation


# Create a violin plot for each category with adjusted width and scale
p_prot <- ggplot(nutrition_df, aes(x = reorder(Category_1, Protein, FUN = median), y = Protein)) +
  geom_violin(trim = FALSE, scale = "width", fill = "black", alpha=0.5) +
  geom_boxplot(width=0.25, alpha=0.5)+
  labs(x = "", y = "Protein (g) per 100 grams or ml", title = "Distribution of Protein by Category") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1),
        plot.title = element_text(hjust = 0.5)) +
  coord_flip()  # Flip coordinates for horizontal orientation


# Create a violin plot for each category with adjusted width and scale
p_prot <- ggplot(nutrition_df, aes(x = reorder(Category_1, Protein, FUN = median), y = Protein)) +
  geom_violin(trim = FALSE, scale = "width", fill = "black", alpha=0.5) +
  geom_boxplot(width=0.25, alpha=0.5)+
  labs(x = "", y = "Protein (g) per 100 grams or ml", title = "Distribution of Protein by Category") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1),
        plot.title = element_text(hjust = 0.5)) +
  coord_flip()  # Flip coordinates for horizontal orientation


p_fats <- ggplot(nutrition_df, aes(x = reorder(Category_1, Fats, FUN = median), y = Fats)) +
  geom_violin(trim = FALSE, scale = "width", fill = "black", alpha=0.5) +
  geom_boxplot(width=0.25, alpha=0.5)+
  labs(x = "", y = "Fat (g) per 100 grams or ml", title = "Distribution of Fat by Category") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1),
        plot.title = element_text(hjust = 0.5)) +
  coord_flip()  # Flip coordinates for horizontal orientation


ggsave(filename = "calorie_distributions.png", plot = p_cal, width = 540/72, height = 340/72, dpi = 300, units = "in", bg = "white")
ggsave(filename = "carb_distributions.png", plot = p_carb, width = 540/72, height = 340/72, dpi = 300, units = "in", bg = "white")
ggsave(filename = "protein_distributions.png", plot = p_prot, width = 540/72, height = 340/72, dpi = 300, units = "in", bg = "white")
ggsave(filename = "fats_distributions.png", plot = p_fats, width = 540/72, height = 340/72, dpi = 300, units = "in", bg = "white")

# Load necessary libraries
library(dplyr)

# Count unique subcategories at each level for each main category
category_overview <- df %>%
  group_by(Category_1, Category_2, Category_3, Category_4, Category_5, Category_6) %>%
  summarise(count = n()) %>%
  arrange(Category_1, Category_2, Category_3, Category_4, Category_5, Category_6)

# Display the overview
print(category_overview)



