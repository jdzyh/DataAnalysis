#install.packages('ggplot2', dependencies = T)
library(ggplot2)
data("diamonds")

summary(diamonds)
names(diamonds)
str(diamonds)

#plot1
ggplot(data=diamonds, aes(x=diamonds$price)) + 
  geom_histogram(binwidth = 500) + 
  scale_x_continuous()

summary(diamonds$price)

subset(diamonds, price>=15000)

#plot peak of plot
ggplot(data=diamonds, aes(x=diamonds$price)) + 
  geom_histogram(binwidth = 1) + 
  coord_cartesian(xlim=c(0,2500))


#plot price split by cut level
ggplot(data=diamonds, aes(x=diamonds$price)) + 
  geom_histogram(binwidth = 5) + 
  coord_cartesian(xlim=c(300,400), ylim=c(2,4)) +
  facet_wrap(~cut, ncol=3)

#get median
qplot(data=diamonds, y=diamonds$price, x=cut, geom='boxplot')+
  coord_cartesian(ylim=c(0, 10000))
  
#get max and min
subset(diamonds, price==max(diamonds$price))
subset(diamonds, price==min(diamonds$price))

#
qplot(x = price, data = diamonds) + facet_wrap(~cut)
summary(diamonds$price, cut='Ideal')

