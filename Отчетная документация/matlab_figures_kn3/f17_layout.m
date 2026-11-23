% Рисунок: принцип разделения модуля ПОС на экранированные отсеки (без масштаба)
h = fig_new(16,9); axes('Position',[0 0 1 1]); hold on; axis off; xlim([0 100]); ylim([-3 63]);
rectangle('Position',[2 2 96 56],'LineWidth',2.5);
rectangle('Position',[5 32 30 23],'FaceColor',[0.88 0.94 1],'LineWidth',1.5); text(5+30/2,32+23/2,{'Отсек аналогового тракта','4 × AD8367, фильтры ПЧ,','трансформаторы, входы SMA'},'HorizontalAlignment','center','FontSize',8);
rectangle('Position',[39 5 56 50],'FaceColor',[0.92 1 0.92],'LineWidth',1.5); text(39+56/2,5+50/2,{'Отсек цифровой части','К5119ПВ1Я, XC7Z030, HMC7044,','DDR3, QSPI, STM32, KSZ9893'},'HorizontalAlignment','center','FontSize',8);
rectangle('Position',[5 5 30 23],'FaceColor',[1 0.93 0.85],'LineWidth',1.5); text(5+30/2,5+23/2,{'Отсек входной цепи питания','защита, фильтр ЭМС,','DC/DC 24→12 В, накопитель'},'HorizontalAlignment','center','FontSize',8);
plot([20 20],[55 60],'k','LineWidth',2); text(21,60.3,'ввод ПЧ (коаксиальный, экран по кругу)','FontSize',7);
plot([20 20],[0 5],'k','LineWidth',2); text(21,-0.6,'ввод 24 В через проходной фильтр','FontSize',7);
plot([95 100],[40 40],'k','LineWidth',2); text(84,42,'оптика Ethernet','FontSize',7);
plot([95 100],[20 20],'k','LineWidth',2); text(84,22,'CAN, «Отказ»','FontSize',7);
plot([35 39],[43 43],'b','LineWidth',2); text(35.3,45.5,'ПЧ','FontSize',7,'Color','b');
plot([35 39],[15 15],'r','LineWidth',2); text(34.6,17.5,'питание','FontSize',7,'Color','r');
plot(37,30,'kp','MarkerSize',12,'MarkerFaceColor','k'); text(30.5,30,'точка соединения земель','FontSize',7,'HorizontalAlignment','right');
fig_save(h,'f17_layout');
