% Рисунок: скорость линии JESD204B по режимам передачи и пределы GTX
Np = 16; L = 4; Fs = 400e6;
mode = {'2 канала, без децимации','4 канала, без децимации','4 канала, децимация 2 (комплексные)','4 канала, децимация 4 (комплексные)'};
M = [2 4 8 8]; Fo = [Fs Fs Fs/2 Fs/4];
R = M.*Np.*Fo/L*10/8/1e9;
h = fig_new(16,7.5); hold on; box on; grid on;
barh(1:4, R, 0.6, 'FaceColor', [0.3 0.5 0.8]);
plot([8 8],[0.4 4.6],'r--','LineWidth',1.5); plot([10.3125 10.3125],[0.4 4.6],'Color',[0 0.6 0],'LineStyle','--','LineWidth',1.5);
plot([6.6 6.6],[0.4 4.6],'Color',[0.5 0.5 0.5],'LineStyle',':','LineWidth',1.5);
for k=1:4, text(R(k)+0.1,k,rus(sprintf('%.1f',R(k)))); end
set(gca,'YTick',1:4,'YTickLabel',mode); xlim([0 12]); ylim([0.4 4.6]);
xlabel('Скорость линии, Гбит/с');
legend({'расчёт скорости линии','−1I, QPLL: 8,0','−2I, QPLL: 10,3125','CPLL −1I: 6,6'},'Location','southoutside','NumColumns',2);
fig_save(h,'f18_jesd');
