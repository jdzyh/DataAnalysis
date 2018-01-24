#Lesson 6
#========================================================

library('ggplot2')
data(diamonds)

summary(diamonds)

ggplot(aes(x=carat, y=price), data=diamonds)+
  xlim(0, quantile(diamonds$carat, 0.99))+
  ylim(0, quantile(diamonds$price, 0.99))+
  geom_point(alpha=1/4)+
  stat_smooth(method='lm') #添加统计平滑函数:linear model

#install.packages('GGally')
#install.packages('scales')
#install.packages('memisc')
#install.packages('lattice')
#install.packages('MASS')
#install.packages('car')
#install.packages('reshape')
#install.packages('plyr')

# load the ggplot graphics package and the others
library(ggplot2)
library(GGally)
library(scales)
library(memisc)

# sample 10,000 diamonds from the data set
set.seed(20022012)
diamond_samp <- diamonds[sample(1:length(diamonds$price), 10000), ]
ggpairs(diamond_samp, 
        lower = list(continuous = wrap("points", shape = I('.'))), 
        upper = list(combo = wrap("box", outlier.shape = I('.'))))

# Log trans
library(gridExtra)
library(grid)
plot1 <- ggplot(data=diamonds, aes(x=price))+
  geom_histogram(binwidth = 100, fill=I('#099D09'))+
  ggtitle('Price')

plot2 <- ggplot(data=diamonds, aes(x=price))+
  scale_x_log10()+
  geom_histogram(binwidth = 0.01, fill=I('#F79420'))+
  ggtitle('Price(log10)')
# 双峰类型的数据（正态型），穷人与富人两类目标用户
grid.arrange(plot1, plot2, ncol=2)

#按照cut 类型作图
ggplot(data=diamonds, aes(x=price))+
  scale_x_log10()+
  geom_histogram(binwidth = 0.01, fill=I('#099DD9'))+
  facet_wrap(~cut, ncol=3)

# 尝试对price取对数
ggplot(data=diamonds, aes(x=carat, y=price))+
  scale_y_continuous(trans = log10_trans())+
  geom_point()+
  ggtitle('Price(log10) by Carat')
### Create a new function to transform the carat variable
cuberoot_trans = function() trans_new('cuberoot', transform = function(x) x^(1/3),
                                      inverse = function(x) x^3)
#### Use the cuberoot_trans function
#返回的图像有近似线性的x-y关系
ggplot(aes(carat, price), data = diamonds) + 
  geom_point() + 
  scale_x_continuous(trans = cuberoot_trans(), limits = c(0.2, 3),
                     breaks = c(0.2, 0.5, 1, 2, 3)) + 
  scale_y_continuous(trans = log10_trans(), limits = c(350, 15000),
                     breaks = c(350, 1000, 5000, 10000, 15000)) +
  ggtitle('Price (log10) by Cube-Root of Carat')


### Overplotting Revisited
# 同一个值有多个样本，
#会导致在绘制时叠加，
#从而丢弃数据的密度信息
head(sort(table(diamonds$carat), decreasing=T))
head(sort(table(diamonds$price), decreasing=T))

ggplot(aes(carat, price), data = diamonds) + 
  geom_point(alpha=0.5, size=0.75, position='jitter') + 
  scale_x_continuous(trans = cuberoot_trans(), limits = c(0.2, 3),
                     breaks = c(0.2, 0.5, 1, 2, 3)) + 
  scale_y_continuous(trans = log10_trans(), limits = c(350, 15000),
                     breaks = c(350, 1000, 5000, 10000, 15000)) +
  ggtitle('Price (log10) by Cube-Root of Carat')


### Price vs. Carat and Clarity
install.packages('RColorBrewer')
library(RColorBrewer)

ggplot(aes(x = carat, y = price, color=clarity), data = diamonds) + 
  geom_point(alpha = 0.5, size = 1, position = 'jitter') +
  scale_color_brewer(type = 'div',
    guide = guide_legend(title = 'Clarity', reverse = T,
    override.aes = list(alpha = 1, size = 2))) +  
  scale_x_continuous(trans = cuberoot_trans(), limits = c(0.2, 3),
    breaks = c(0.2, 0.5, 1, 2, 3)) + 
  scale_y_continuous(trans = log10_trans(), limits = c(350, 15000),
    breaks = c(350, 1000, 5000, 10000, 15000)) +
  ggtitle('Price (log10) by Cube-Root of Carat and Clarity')



### Price vs. Carat and Cut
ggplot(aes(x = carat, y = price, color = cut), data = diamonds) + 
  geom_point(alpha = 0.5, size = 1, position = 'jitter') +
  scale_color_brewer(type = 'div',
                     guide = guide_legend(title = 'cut', reverse = T,
                                          override.aes = list(alpha = 1, size = 2))) +  
  scale_x_continuous(trans = cuberoot_trans(), limits = c(0.2, 3),
                     breaks = c(0.2, 0.5, 1, 2, 3)) + 
  scale_y_continuous(trans = log10_trans(), limits = c(350, 15000),
                     breaks = c(350, 1000, 5000, 10000, 15000)) +
  ggtitle('Price (log10) by Cube-Root of Carat and cut')


### Price vs. Carat and Color
ggplot(aes(x = carat, y = price, color = color), data = diamonds) + 
  geom_point(alpha = 0.5, size = 1, position = 'jitter') +
  scale_color_brewer(type = 'div',
                     guide = guide_legend(title = 'color', reverse = F,
                                          override.aes = list(alpha = 1, size = 2))) +  
  scale_x_continuous(trans = cuberoot_trans(), limits = c(0.2, 3),
                     breaks = c(0.2, 0.5, 1, 2, 3)) + 
  scale_y_continuous(trans = log10_trans(), limits = c(350, 15000),
                     breaks = c(350, 1000, 5000, 10000, 15000)) +
  ggtitle('Price (log10) by Cube-Root of Carat and Color')


### Linear Models in R
# http://data.princeton.edu/R/linearModels.html
### Building the Linear Model
m1 <- lm(I(log(price)) ~ I(carat^(1/3)), data = diamonds)
m2 <- update(m1, ~ . + carat)
m3 <- update(m2, ~ . + cut)
m4 <- update(m3, ~ . + color)
m5 <- update(m4, ~ . + clarity)
mtable(m1, m2, m3, m4, m5)


#Notice how adding cut to our model does not help explain much of the variance
#in the price of diamonds. This fits with out exploration earlier.

### A Bigger, Better Data Set
#install.packages('bitops')
#install.packages('RCurl')
library('bitops')
library('RCurl')

#diamondsurl = getBinaryURL("https://raw.github.com/solomonm/diamonds-data/master/BigDiamonds.Rda")
#load(rawConnection(diamondsurl))
load("BigDiamonds.rda")

#The code used to obtain the data is available here:
#https://github.com/solomonm/diamonds-data

## Building a Model Using the Big Diamonds Data Set
diamondsbig$logprice=log(diamondsbig$price)

m1 <- lm(logprice ~ I(carat^(1/3)), 
         data = diamondsbig[diamondsbig$price<10000 & 
                              diamondsbig$cert == "GIA",])
m2 <- update(m1, ~ . + carat)
m3 <- update(m2, ~ . + cut)
m4 <- update(m3, ~ . + color)
m5 <- update(m4, ~ . + clarity)
mtable(m1, m2, m3, m4, m5)
#Be sure you have loaded the library memisc and have m5 saved as an object in your workspace.
thisDiamond = data.frame(carat = 1.00, cut = "V.Good",
                         color = "I", clarity="VS1")
modelEstimate = predict(m5, newdata = thisDiamond,
                        interval="prediction", level = .95)
exp(modelEstimate)
#Evaluate how well the model predicts the BlueNile diamond's price. Think about the fitted point estimate as well as the 95% CI.

#Click **KnitHTML** to see all of your hard work and to have an html
#page of this lesson, your answers, and your notes!
