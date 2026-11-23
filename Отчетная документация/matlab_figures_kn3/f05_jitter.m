% Рисунок: добавочная потеря ОСШ от джиттера тактового сигнала
sig = linspace(50,600,500)*1e-15; f = [60e6 70e6]; qa = [62 65];
h = fig_new(16,8); hold on; box on; grid on;
st = {'-','--'}; cl = {'b','r'}; leg = {};
for i = 1:2
  for j = 1:2
    qj = 20*log10(1./(2*pi*f(j)*sig));
    qs = -10*log10(10.^(-qa(i)/10)+10.^(-qj/10));
    plot(sig*1e15, qa(i)-qs, 'LineStyle', st{j}, 'Color', cl{i});
    leg{end+1} = sprintf('q_{АЦП} = %d дБпш, f = %d МГц', qa(i), f(j)/1e6);
  end
end
plot([50 600],[0.1 0.1],'k:','LineWidth',1.5); leg{end+1} = 'допустимая потеря 0,1 дБ';
plot([330 330],[0 1],'Color',[0.5 0.5 0.5],'LineStyle','-.'); leg{end+1} = '\sigma = 330 фс';
ylim([0 0.6]); xlabel('СКЗ джиттера \sigma, фс'); ylabel('Потеря ОСШ, дБ');
legend(leg,'Location','northwest');
fig_save(h,'f05_jitter');
