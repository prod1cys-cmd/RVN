% Рисунок: частотный план тактирования модуля (HMC7044, ГУН 2400 МГц)
h = fig_new(16,8); axes('Position',[0 0 1 1]); hold on; axis off; xlim([0 100]); ylim([0 50]);
rectangle('Position',[3 30 18 12],'FaceColor',[0.95 0.95 0.95],'LineWidth',1.2); text(12,36,{'Опора 100 МГц','(генератор модуля','или вход SMA)'},'HorizontalAlignment','center','FontSize',8);
rectangle('Position',[26 26 24 20],'FaceColor',[0.88 0.94 1],'LineWidth',1.5); text(38,36,{'HMC7044','ФАПЧ1 → ГУН 100 МГц','ФАПЧ2 → ГУН 2400 МГц'},'HorizontalAlignment','center','FontSize',8);
plot([21 26],[36 36],'k-','LineWidth',1.5);
out = {'÷6 → 400 МГц: DCLK К5119ПВ1Я','÷6 → 400 МГц: опора GTX (банк 112)','÷768 → 3,125 МГц: SYSREF К5119ПВ1Я','÷768 → 3,125 МГц: SYSREF ПЛИС (банк 34)','÷240 → 10 МГц: контрольный выход','÷48 → 50 МГц: контрольный выход'};
y = linspace(46,4,6);
for k=1:6
  plot([50 58],[36 y(k)],'k-'); plot([58 62],[y(k) y(k)],'k-'); text(62.5,y(k),out{k},'FontSize',8);
end
text(12,20,{'Дискретизация 400 МГц','LMFC: 3,125 МГц (4 Гбит/с)','6,25 МГц (8 Гбит/с)'},'HorizontalAlignment','center','FontSize',8);
fig_save(h,'f19_clock');
