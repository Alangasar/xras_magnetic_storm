# Xras Magnetic Storm

Интеграция для Home Assistant. В HA добавляются три сенсора, текущий Kp-индекс, и два за предыдущие дни. 

Kp-индекс колеблется от 0 до 9, где значение 0 означает отсутствие геомагнитной активности, а значение 9 означает экстремальный геомагнитный шторм.

Данные о магнитной буре берутся с сайта https://xras.ru/ 

## Установка
### Вариант 1 - HACS
Перейти в HACS -> Интеграции -> Пользовательские репозитории. Добавить репозиторий https://github.com/Alangasar/xras_magnetic_storm в HACS.
Перезагрузить HA.
Добавить интеграцию "Xras Magnetic Storm" на странице Настройки -> Устройства и службы.
### Вариант 2 - Ручная установка
Cкопировать каталог magnetic_storm в каталог custom_components.
Перезагрузить HA.
Добавить интеграцию "Xras Magnetic Storm" на странице Настройки -> Устройства и службы.

### Список поддерживаемых городов
1. Абакан  
2. Анадырь  
3. Архангельск  
4. Астрахань  
5. Барнаул  
6. Белгород  
7. Биробиджан  
8. Благовещенск  
9. Братск  
10. Брянск  
11. Владивосток  
12. Владикавказ  
13. Владимир  
14. Волгоград  
15. Вологда  
16. Воркута  
17. Воронеж  
18. Горно-Алтайск  
19. Грозный  
20. Екатеринбург  
21. Иваново  
22. Ижевск  
23. Иркутск  
24. Йошкар-Ола  
25. Казань  
26. Калининград  
27. Калуга  
28. Кемерово  
29. Киров  
30. Кишинёв  
31. Комсомольск-на-Амуре  
32. Кострома  
33. Краснодар  
34. Красноярск  
35. Курган  
36. Курск  
37. Кызыл  
38. Ленск  
39. Липецк  
40. Магадан  
41. Майкоп  
42. Махачкала  
43. Мещовск  
44. Минеральные Воды  
45. Мирный (Якутия)  
46. Москва  
47. Мурманск  
48. Набережные Челны  
49. Назрань  
50. Нальчик  
51. Нерюнгри  
52. Нижневартовск  
53. Нижний Новгород  
54. Новгород  
55. Новокузнецк  
56. Новосибирск  
57. Новый Уренгой  
58. Норильск  
59. Омск  
60. Оренбург  
61. Орёл  
62. Пенза  
63. Пермь  
64. Петрозаводск  
65. Петропавловск-Камчатский  
66. Псков  
67. Ростов-на-Дону  
68. Рязань  
69. Салехард  
70. Самара  
71. Санкт-Петербург  
72. Саранск  
73. Саратов  
74. Симферополь  
75. Смоленск  
76. Сочи  
77. Ставрополь  
78. Станция Восток  
79. Станция Мирный  
80. Сургут  
81. Сыктывкар  
82. Тамбов  
83. Тверь  
84. Тикси  
85. Тольятти  
86. Томск  
87. Тула  
88. Тюмень  
89. Улан-Удэ  
90. Ульяновск  
91. Уфа  
92. Хабаровск  
93. Ханты-Мансийск  
94. Чебоксары  
95. Челябинск  
96. Череповец  
97. Черкесск  
98. Чита  
99. Элиста  
100. Южно-Сахалинск  
101. Якутск  
102. Ярославль  
