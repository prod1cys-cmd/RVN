% Рисунок: временная диаграмма зондирования для двух крайних шкал (Книга 1, табл. 1.3)
c = 299792458; mile = 1852;
sc   = [1.5 96];         % шкала, мили
tau  = [0.07 1.2]*1e-6;  % длительность импульса, с
Fpov = [3000 500];       % ЧПИ, Гц
h = fig_new(16,9);
for k = 1:2
  subplot(2,1,k); hold on; box on; grid on;
  T = 1/Fpov(k); tR = 2*sc(k)*mile/c;
  patch([0 tR tR 0]*1e6,[0 0 1.15 1.15],[0.85 0.92 1],'EdgeColor','none');
  t = linspace(-0.05*T, 1.08*T, 20000);
  u = double(mod(t,T) < tau(k));
  stairs(t*1e6, u, 'b', 'LineWidth', 1.5);
  plot([tR tR]*1e6,[0 1.15],'r--');
  xlim([-0.05*T 1.08*T]*1e6); ylim([0 1.25]);
  ylabel('u/U_m'); xlabel('Время, мкс');
  title(rus(sprintf('Шкала %g миль: \\tau = %g мкс, F = %d Гц, T = %.1f мкс, задержка эха %.1f мкс', ...
        sc(k), tau(k)*1e6, Fpov(k), T*1e6, tR*1e6)));
  text(max(tR*1e6*0.5, 0.12*T*1e6), 1.07, 'окно приёма эхо-сигналов', 'HorizontalAlignment','center');
end
fig_save(h,'f01_pulses');
