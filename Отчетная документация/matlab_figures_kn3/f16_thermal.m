% Рисунок: температура перехода СнК в зависимости от рассеиваемой мощности
Ta = 70; Tj = 100; P = linspace(0,10,200); th = [3 5 7 10];
h = fig_new(16,8); hold on; box on; grid on; leg = {};
for k = 1:numel(th)
  plot(P, Ta + th(k)*P); leg{end+1} = sprintf('\\Theta_{ja} = %d °C/Вт', th(k));
end
plot([0 10],[Tj Tj],'r--','LineWidth',1.5); leg{end+1} = 'T_{j макс} = 100 °C';
for k = 1:numel(th), plot((Tj-Ta)/th(k), Tj, 'ko','MarkerFaceColor','k'); end
ylim([60 140]); xlabel('Мощность, рассеиваемая СнК, Вт'); ylabel('T_j, °C');
legend(leg,'Location','northwest'); title('Температура среды 70 °C, без запаса и взаимного нагрева');
fig_save(h,'f16_thermal');
