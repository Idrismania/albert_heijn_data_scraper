library(ggplot2)

filtered_food_df <- food_df[complete.cases(food_df[, c("Carbohydrates", "Protein", "Fats")]), c(1, 10, 11, 14, 17, 4, 5, 6, 7, 8, 9)]

# Fit a linear regression model
model <- lm(Energy..kcal. ~ Carbohydrates + Fats + Protein, data = filtered_food_df)

# y at x-intercept and weights for carbs fats andprotein
estimate_weights <- model$coefficients

filtered_food_df$kcal.estimation <- filtered_food_df$Carbohydrates*estimate_weights[2] + filtered_food_df$Fats*estimate_weights[3] + filtered_food_df$Protein*estimate_weights[4] + estimate_weights[1]
filtered_food_df$estimation.difference <- filtered_food_df$kcal.estimation-filtered_food_df$Energy..kcal.

p <- ggplot(data = filtered_food_df, aes(x=Energy..kcal., y=kcal.estimation))+
  geom_point(alpha=0.25)+
  xlim(0, 1000)+
  xlab("Energy (kcal)")+
  ylab("Estimated calories (kcal)")+
  ggtitle("True vs Estimated Caloric energy")+
  theme(
    text = element_text(size=16),
    axis.text = element_text(size=16)
    )
p
#ggsave(filename = "correlation.png", plot = p, width = 350/72, height = 225/72, dpi = 300, units = "in")