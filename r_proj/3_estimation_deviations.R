library(ggplot2)


# Subset data frames based on categories
df_wine <- filtered_food_df[filtered_food_df$Category_1 == "Wijn en bubbels", ]
df_gum <- filtered_food_df[filtered_food_df$Category_2 == "Kauwgom", ]
df_peppermint <- filtered_food_df[filtered_food_df$Category_2 == "Pepermunt, keelpastilles", ]

# Filter out rows not in gum, wine, or peppermint categories
df_no_gum_and_wine <- filtered_food_df[
  !(filtered_food_df$Category_2 %in% c("Kauwgom", "Pepermunt, keelpastilles")) &
    !(filtered_food_df$Category_1 == "Wijn en bubbels"), ]

# Plotting
p <- ggplot() +
  geom_point(data = df_no_gum_and_wine, aes(x = Energy..kcal., y = kcal.estimation, color = "black"), alpha = 0.25) +
  geom_point(data = df_gum, aes(x = Energy..kcal., y = kcal.estimation, color = "blue"), alpha = 0.25) +
  geom_point(data = df_wine, aes(x = Energy..kcal., y = kcal.estimation, color = "red"), alpha = 0.25) +
  geom_point(data = df_peppermint, aes(x = Energy..kcal., y = kcal.estimation, color = "green"), alpha = 0.25) +
  xlim(0, 1000) +
  xlab("Energy (kcal)") +
  ylab("Estimated calories (kcal)") +
  ggtitle("True vs Estimated Caloric energy") +
  theme(
    text = element_text(size = 16),
    axis.text = element_text(size = 16),
    legend.position = "right"
  ) +
  scale_color_manual(
    values = c("black", "blue", "red", "green"),
    labels = c("General", "Gum", "Wine", "Peppermint"),
    name = ""
  )+
  guides(color = guide_legend(override.aes = list(size=3)))

# Save plot
ggsave(filename = "correlation_categorized.png", plot = p, width = 350/72, height = 225/72, dpi = 300, units = "in")
