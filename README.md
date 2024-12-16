# Библиотека приборов

**Проблема:** 

- На предприятии довольно сложно администрировать расположение приборов. Очень часто люди переносят приборы из кабинета в кабинет с целями от быстрого измерения напряжения на печатной плате до установки в стенд на несколько месяцев. Приборами пользуется несколько десятков человек, а приборов около сотни. Не все помнят, когда и куда унесли очередной прибор. Возникают проблемы с отслеживанием и поиском приборов по предприятию. Записываться в единую тетрадку и администрироваться специальным человеком показалось не современным.

**Описание решения проблемы:**

- Для отслеживания приборов был создан бот, с помощью которого может будет записывать прибор на себя и указывать в какую комнату он отправляется. Для ускорения идентификации прибора было решено воспользоваться QR-кодами,
которые предварительно наклееваются на прибор. 
- Суть работы бота:
    * Пользователь регистрируется в боте
    * Для манипуляций с прибором (редактирование характеристик, перемещения, просмотра сведений или добавления в базу) отправляет прибор
    * Для поиска устройства, просто вводит тип параметра, по которому производится поиск и сам параметр

P.S. При переносе проекта на удаленный сервер на Linux помимо установки пакетов из requirements.txt понадобилось так же sudo apt-get install zbar-tools
