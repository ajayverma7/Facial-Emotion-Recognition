# Data Visualization Script for Emotion Recognition System
# Advanced visualizations and interactive plots
# Author: College Project - Facial Emotion Recognition System

# Load required libraries
if (!require("ggplot2")) install.packages("ggplot2")
if (!require("plotly")) install.packages("plotly")
if (!require("dplyr")) install.packages("dplyr")
if (!require("tidyr")) install.packages("tidyr")
if (!require("jsonlite")) install.packages("jsonlite")
if (!require("lubridate")) install.packages("lubridate")
if (!require("RColorBrewer")) install.packages("RColorBrewer")
if (!require("gridExtra")) install.packages("gridExtra")
if (!require("corrplot")) install.packages("corrplot")

library(ggplot2)
library(plotly)
library(dplyr)
library(tidyr)
library(jsonlite)
library(lubridate)
library(RColorBrewer)
library(gridExtra)
library(corrplot)

# Set working directory
setwd("..")

# Function to load and prepare data
load_and_prepare_data <- function(json_path = "data/emotions.json") {
  if (!file.exists(json_path)) {
    cat("Database file not found. Creating sample data for visualization...\n")
    return(create_sample_visualization_data())
  }
  
  # Read JSON data
  json_data <- fromJSON(json_path)
  
  if (length(json_data$emotions) == 0) {
    cat("No emotion data found. Creating sample data for visualization...\n")
    return(create_sample_visualization_data())
  }
  
  # Convert to data frame
  emotions_df <- as.data.frame(json_data$emotions)
  
  # Data preprocessing
  emotions_df$timestamp <- as.POSIXct(emotions_df$timestamp, format = "%Y-%m-%dT%H:%M:%S")
  emotions_df$date <- as.Date(emotions_df$timestamp)
  emotions_df$hour <- hour(emotions_df$timestamp)
  emotions_df$day_of_week <- weekdays(emotions_df$date)
  emotions_df$month <- month(emotions_df$timestamp, label = TRUE)
  
  return(emotions_df)
}

# Function to create sample data for visualization
create_sample_visualization_data <- function() {
  set.seed(42)
  n_samples <- 200
  
  emotions <- c("happy", "sad", "angry", "surprise", "neutral", "disgust", "fear")
  sources <- c("webcam", "upload")
  
  # Create realistic temporal patterns
  start_date <- as.POSIXct("2024-01-01 08:00:00")
  timestamps <- seq(from = start_date, by = "2 hours", length.out = n_samples)
  
  # Add some randomness to timestamps
  timestamps <- timestamps + sample(-3600:3600, n_samples, replace = TRUE)
  
  sample_data <- data.frame(
    id = 1:n_samples,
    timestamp = timestamps,
    dominant_emotion = sample(emotions, n_samples, replace = TRUE, 
                             prob = c(0.25, 0.15, 0.12, 0.13, 0.20, 0.08, 0.07)),
    confidence = pmax(50, pmin(98, rnorm(n_samples, 78, 12))),
    source = sample(sources, n_samples, replace = TRUE, prob = c(0.7, 0.3)),
    face_detected = sample(c(TRUE, FALSE), n_samples, replace = TRUE, prob = c(0.95, 0.05))
  )
  
  # Add derived columns
  sample_data$date <- as.Date(sample_data$timestamp)
  sample_data$hour <- hour(sample_data$timestamp)
  sample_data$day_of_week <- weekdays(sample_data$date)
  sample_data$month <- month(sample_data$timestamp, label = TRUE)
  
  return(sample_data)
}

# Function to create emotion distribution visualizations
create_emotion_distributions <- function(data) {
  cat("Creating emotion distribution visualizations...\n")
  
  # 1. Basic emotion frequency bar chart
  emotion_counts <- data %>%
    count(dominant_emotion, sort = TRUE)
  
  p1 <- ggplot(emotion_counts, aes(x = reorder(dominant_emotion, n), y = n, fill = dominant_emotion)) +
    geom_col(alpha = 0.8) +
    coord_flip() +
    labs(title = "Emotion Detection Frequency", 
         x = "Emotion", y = "Count", fill = "Emotion") +
    theme_minimal() +
    scale_fill_brewer(palette = "Set3") +
    theme(legend.position = "none")
  
  # 2. Emotion distribution pie chart with percentages
  emotion_pct <- emotion_counts %>%
    mutate(percentage = round(n / sum(n) * 100, 1))
  
  p2 <- ggplot(emotion_pct, aes(x = "", y = n, fill = dominant_emotion)) +
    geom_bar(stat = "identity", width = 1) +
    coord_polar("y", start = 0) +
    theme_void() +
    labs(title = "Emotion Distribution (%)", fill = "Emotion") +
    scale_fill_brewer(palette = "Set3") +
    geom_text(aes(label = paste0(percentage, "%")), 
              position = position_stack(vjust = 0.5))
  
  # 3. Emotion by source stacked bar chart
  p3 <- ggplot(data, aes(x = dominant_emotion, fill = source)) +
    geom_bar(position = "fill") +
    labs(title = "Emotion Distribution by Source (Proportional)", 
         x = "Emotion", y = "Proportion", fill = "Source") +
    theme_minimal() +
    theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
    scale_fill_manual(values = c("webcam" = "#3498db", "upload" = "#e74c3c"))
  
  # Save plots
  ggsave("r_scripts/plots/emotion_frequency.png", p1, width = 10, height = 6)
  ggsave("r_scripts/plots/emotion_pie_chart.png", p2, width = 8, height = 8)
  ggsave("r_scripts/plots/emotion_by_source.png", p3, width = 10, height = 6)
  
  return(list(frequency = p1, pie = p2, by_source = p3))
}

# Function to create temporal analysis visualizations
create_temporal_visualizations <- function(data) {
  cat("Creating temporal analysis visualizations...\n")
  
  # 1. Daily emotion trends
  daily_trends <- data %>%
    group_by(date, dominant_emotion) %>%
    summarise(count = n(), .groups = 'drop')
  
  p1 <- ggplot(daily_trends, aes(x = date, y = count, color = dominant_emotion)) +
    geom_line(size = 1, alpha = 0.8) +
    geom_point(size = 2, alpha = 0.6) +
    labs(title = "Daily Emotion Trends Over Time", 
         x = "Date", y = "Count", color = "Emotion") +
    theme_minimal() +
    scale_color_brewer(palette = "Set2") +
    theme(legend.position = "bottom")
  
  # 2. Hourly patterns heatmap
  hourly_data <- data %>%
    group_by(hour, dominant_emotion) %>%
    summarise(count = n(), .groups = 'drop')
  
  p2 <- ggplot(hourly_data, aes(x = hour, y = dominant_emotion, fill = count)) +
    geom_tile(color = "white") +
    labs(title = "Emotion Detection Patterns by Hour", 
         x = "Hour of Day", y = "Emotion", fill = "Count") +
    theme_minimal() +
    scale_fill_gradient(low = "lightblue", high = "darkblue") +
    scale_x_continuous(breaks = seq(0, 23, 2))
  
  # 3. Day of week patterns
  dow_data <- data %>%
    group_by(day_of_week, dominant_emotion) %>%
    summarise(count = n(), .groups = 'drop') %>%
    mutate(day_of_week = factor(day_of_week, 
                               levels = c("Monday", "Tuesday", "Wednesday", 
                                        "Thursday", "Friday", "Saturday", "Sunday")))
  
  p3 <- ggplot(dow_data, aes(x = day_of_week, y = count, fill = dominant_emotion)) +
    geom_col(position = "dodge") +
    labs(title = "Emotion Detection by Day of Week", 
         x = "Day of Week", y = "Count", fill = "Emotion") +
    theme_minimal() +
    theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
    scale_fill_brewer(palette = "Set3")
  
  # Save plots
  ggsave("r_scripts/plots/daily_trends.png", p1, width = 12, height = 6)
  ggsave("r_scripts/plots/hourly_heatmap.png", p2, width = 10, height = 6)
  ggsave("r_scripts/plots/day_of_week_patterns.png", p3, width = 12, height = 6)
  
  return(list(daily = p1, hourly = p2, dow = p3))
}

# Function to create confidence analysis visualizations
create_confidence_visualizations <- function(data) {
  cat("Creating confidence analysis visualizations...\n")
  
  # 1. Confidence distribution histogram
  p1 <- ggplot(data, aes(x = confidence)) +
    geom_histogram(bins = 30, fill = "skyblue", alpha = 0.7, color = "black") +
    geom_vline(aes(xintercept = mean(confidence)), color = "red", linetype = "dashed", size = 1) +
    labs(title = "Confidence Score Distribution", 
         x = "Confidence (%)", y = "Frequency") +
    theme_minimal() +
    annotate("text", x = mean(data$confidence) + 5, y = Inf, 
             label = paste("Mean:", round(mean(data$confidence), 1), "%"), 
             vjust = 2, color = "red")
  
  # 2. Confidence by emotion box plot
  p2 <- ggplot(data, aes(x = reorder(dominant_emotion, confidence, median), 
                        y = confidence, fill = dominant_emotion)) +
    geom_boxplot(alpha = 0.7) +
    geom_jitter(width = 0.2, alpha = 0.3) +
    labs(title = "Confidence Distribution by Emotion", 
         x = "Emotion", y = "Confidence (%)") +
    theme_minimal() +
    theme(axis.text.x = element_text(angle = 45, hjust = 1),
          legend.position = "none") +
    scale_fill_brewer(palette = "Set3")
  
  # 3. Confidence vs Time scatter plot
  p3 <- ggplot(data, aes(x = timestamp, y = confidence, color = dominant_emotion)) +
    geom_point(alpha = 0.6, size = 2) +
    geom_smooth(method = "loess", se = FALSE, color = "black", linetype = "dashed") +
    labs(title = "Confidence Trends Over Time", 
         x = "Time", y = "Confidence (%)", color = "Emotion") +
    theme_minimal() +
    scale_color_brewer(palette = "Set2")
  
  # Save plots
  ggsave("r_scripts/plots/confidence_distribution.png", p1, width = 10, height = 6)
  ggsave("r_scripts/plots/confidence_by_emotion.png", p2, width = 10, height = 6)
  ggsave("r_scripts/plots/confidence_trends.png", p3, width = 12, height = 6)
  
  return(list(distribution = p1, by_emotion = p2, trends = p3))
}

# Function to create advanced statistical visualizations
create_advanced_visualizations <- function(data) {
  cat("Creating advanced statistical visualizations...\n")
  
  # 1. Correlation matrix of emotion frequencies by hour
  emotion_hour_matrix <- data %>%
    group_by(hour, dominant_emotion) %>%
    summarise(count = n(), .groups = 'drop') %>%
    pivot_wider(names_from = dominant_emotion, values_from = count, values_fill = 0)
  
  # Create correlation matrix
  cor_matrix <- cor(emotion_hour_matrix[, -1])
  
  # Save correlation plot
  png("r_scripts/plots/emotion_correlation_matrix.png", width = 800, height = 600)
  corrplot(cor_matrix, method = "color", type = "upper", 
           title = "Emotion Co-occurrence Correlation Matrix",
           mar = c(0, 0, 1, 0))
  dev.off()
  
  # 2. Density plot of confidence by emotion
  p2 <- ggplot(data, aes(x = confidence, fill = dominant_emotion)) +
    geom_density(alpha = 0.6) +
    facet_wrap(~dominant_emotion, scales = "free_y") +
    labs(title = "Confidence Density Distribution by Emotion", 
         x = "Confidence (%)", y = "Density") +
    theme_minimal() +
    theme(legend.position = "none") +
    scale_fill_brewer(palette = "Set3")
  
  # 3. Violin plot for confidence distribution
  p3 <- ggplot(data, aes(x = reorder(dominant_emotion, confidence, median), 
                        y = confidence, fill = dominant_emotion)) +
    geom_violin(alpha = 0.7, trim = FALSE) +
    geom_boxplot(width = 0.1, alpha = 0.8) +
    labs(title = "Confidence Distribution (Violin Plot)", 
         x = "Emotion", y = "Confidence (%)") +
    theme_minimal() +
    theme(axis.text.x = element_text(angle = 45, hjust = 1),
          legend.position = "none") +
    scale_fill_brewer(palette = "Set3")
  
  # Save plots
  ggsave("r_scripts/plots/confidence_density.png", p2, width = 12, height = 8)
  ggsave("r_scripts/plots/confidence_violin.png", p3, width = 10, height = 6)
  
  return(list(correlation = cor_matrix, density = p2, violin = p3))
}

# Function to create interactive visualizations
create_interactive_visualizations <- function(data) {
  cat("Creating interactive visualizations...\n")
  
  # 1. Interactive emotion timeline
  daily_summary <- data %>%
    group_by(date, dominant_emotion) %>%
    summarise(count = n(), avg_confidence = mean(confidence), .groups = 'drop')
  
  p1 <- plot_ly(daily_summary, x = ~date, y = ~count, color = ~dominant_emotion,
                type = 'scatter', mode = 'lines+markers',
                hovertemplate = paste('<b>%{fullData.name}</b><br>',
                                    'Date: %{x}<br>',
                                    'Count: %{y}<br>',
                                    'Avg Confidence: %{text}%<extra></extra>'),
                text = ~round(avg_confidence, 1)) %>%
    layout(title = "Interactive Emotion Timeline",
           xaxis = list(title = "Date"),
           yaxis = list(title = "Count"))
  
  htmlwidgets::saveWidget(p1, "r_scripts/plots/interactive_timeline.html")
  
  # 2. Interactive confidence scatter plot
  p2 <- plot_ly(data, x = ~timestamp, y = ~confidence, color = ~dominant_emotion,
                type = 'scatter', mode = 'markers',
                hovertemplate = paste('<b>%{fullData.name}</b><br>',
                                    'Time: %{x}<br>',
                                    'Confidence: %{y}%<br>',
                                    'Source: %{text}<extra></extra>'),
                text = ~source) %>%
    layout(title = "Interactive Confidence Analysis",
           xaxis = list(title = "Time"),
           yaxis = list(title = "Confidence (%)"))
  
  htmlwidgets::saveWidget(p2, "r_scripts/plots/interactive_confidence.html")
  
  # 3. Interactive 3D emotion analysis
  hourly_emotion_conf <- data %>%
    group_by(hour, dominant_emotion) %>%
    summarise(count = n(), avg_confidence = mean(confidence), .groups = 'drop')
  
  p3 <- plot_ly(hourly_emotion_conf, x = ~hour, y = ~dominant_emotion, z = ~avg_confidence,
                color = ~count, type = 'scatter3d', mode = 'markers',
                marker = list(size = ~count/2),
                hovertemplate = paste('Hour: %{x}<br>',
                                    'Emotion: %{y}<br>',
                                    'Avg Confidence: %{z}%<br>',
                                    'Count: %{marker.color}<extra></extra>')) %>%
    layout(title = "3D Emotion Analysis (Hour vs Emotion vs Confidence)",
           scene = list(xaxis = list(title = "Hour"),
                       yaxis = list(title = "Emotion"),
                       zaxis = list(title = "Avg Confidence (%)")))
  
  htmlwidgets::saveWidget(p3, "r_scripts/plots/interactive_3d_analysis.html")
  
  cat("Interactive visualizations saved as HTML files\n")
  
  return(list(timeline = p1, confidence = p2, analysis_3d = p3))
}

# Function to create summary dashboard
create_summary_dashboard <- function(data) {
  cat("Creating summary dashboard...\n")
  
  # Calculate key metrics
  total_detections <- nrow(data)
  avg_confidence <- round(mean(data$confidence), 1)
  most_common_emotion <- names(sort(table(data$dominant_emotion), decreasing = TRUE))[1]
  date_range <- paste(min(data$date), "to", max(data$date))
  
  # Create summary statistics
  summary_stats <- data %>%
    group_by(dominant_emotion) %>%
    summarise(
      count = n(),
      percentage = round(n() / nrow(data) * 100, 1),
      avg_confidence = round(mean(confidence), 1),
      .groups = 'drop'
    ) %>%
    arrange(desc(count))
  
  # Create dashboard plot
  p1 <- ggplot(summary_stats, aes(x = reorder(dominant_emotion, count), y = count)) +
    geom_col(aes(fill = avg_confidence), alpha = 0.8) +
    geom_text(aes(label = paste0(count, " (", percentage, "%)")), 
              hjust = -0.1, size = 3) +
    coord_flip() +
    labs(title = paste("Emotion Recognition Dashboard"),
         subtitle = paste("Total Detections:", total_detections, 
                         "| Avg Confidence:", avg_confidence, "%",
                         "| Period:", date_range),
         x = "Emotion", y = "Count", fill = "Avg Confidence (%)") +
    theme_minimal() +
    scale_fill_gradient(low = "lightcoral", high = "darkgreen") +
    theme(plot.title = element_text(size = 16, face = "bold"),
          plot.subtitle = element_text(size = 12))
  
  ggsave("r_scripts/plots/summary_dashboard.png", p1, width = 12, height = 8)
  
  return(list(dashboard = p1, summary_stats = summary_stats))
}

# Main visualization function
main_visualization <- function() {
  cat("Starting Data Visualization Analysis...\n")
  
  # Create output directories
  dir.create("r_scripts/plots", showWarnings = FALSE, recursive = TRUE)
  
  # Load and prepare data
  data <- load_and_prepare_data()
  
  # Create all visualizations
  emotion_dist <- create_emotion_distributions(data)
  temporal_viz <- create_temporal_visualizations(data)
  confidence_viz <- create_confidence_visualizations(data)
  advanced_viz <- create_advanced_visualizations(data)
  interactive_viz <- create_interactive_visualizations(data)
  dashboard <- create_summary_dashboard(data)
  
  # Generate visualization report
  generate_visualization_report(data, dashboard$summary_stats)
  
  cat("\nVisualization analysis completed successfully!\n")
  cat("Check the following outputs:\n")
  cat("- Static plots: r_scripts/plots/*.png\n")
  cat("- Interactive plots: r_scripts/plots/*.html\n")
  cat("- Report: r_scripts/visualization_report.txt\n")
  
  return(list(
    data = data,
    emotion_distributions = emotion_dist,
    temporal_visualizations = temporal_viz,
    confidence_visualizations = confidence_viz,
    advanced_visualizations = advanced_viz,
    interactive_visualizations = interactive_viz,
    dashboard = dashboard
  ))
}

# Function to generate visualization report
generate_visualization_report <- function(data, summary_stats) {
  report_file <- "r_scripts/visualization_report.txt"
  
  sink(report_file)
  
  cat("DATA VISUALIZATION ANALYSIS REPORT\n")
  cat("Generated on:", format(Sys.time(), "%Y-%m-%d %H:%M:%S"), "\n")
  cat("="*50, "\n\n")
  
  cat("DATASET OVERVIEW\n")
  cat("Total Records:", nrow(data), "\n")
  cat("Date Range:", as.character(min(data$date)), "to", as.character(max(data$date)), "\n")
  cat("Average Confidence:", round(mean(data$confidence), 2), "%\n")
  cat("Unique Emotions:", length(unique(data$dominant_emotion)), "\n\n")
  
  cat("EMOTION SUMMARY STATISTICS\n")
  print(summary_stats)
  cat("\n")
  
  cat("VISUALIZATIONS CREATED\n")
  cat("1. Emotion Distribution Charts (frequency, pie chart, by source)\n")
  cat("2. Temporal Analysis (daily trends, hourly heatmap, day-of-week patterns)\n")
  cat("3. Confidence Analysis (distribution, by emotion, trends over time)\n")
  cat("4. Advanced Statistics (correlation matrix, density plots, violin plots)\n")
  cat("5. Interactive Visualizations (timeline, confidence scatter, 3D analysis)\n")
  cat("6. Summary Dashboard\n\n")
  
  cat("KEY INSIGHTS\n")
  most_common <- summary_stats$dominant_emotion[1]
  least_common <- summary_stats$dominant_emotion[nrow(summary_stats)]
  highest_conf <- summary_stats$dominant_emotion[which.max(summary_stats$avg_confidence)]
  
  cat("- Most detected emotion:", most_common, 
      "(", summary_stats$percentage[1], "% of detections)\n")
  cat("- Least detected emotion:", least_common, 
      "(", summary_stats$percentage[nrow(summary_stats)], "% of detections)\n")
  cat("- Highest confidence emotion:", highest_conf, 
      "(", max(summary_stats$avg_confidence), "% average confidence)\n")
  
  sink()
  
  cat("Visualization report saved to:", report_file, "\n")
}

# Run the visualization analysis
if (!interactive()) {
  results <- main_visualization()
}
