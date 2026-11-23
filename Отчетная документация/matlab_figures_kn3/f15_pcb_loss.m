% Рисунок: диэлектрические потери в линии 100 мм для двух материалов
c = 299792458; f = linspace(0.1e9,10e9,300); L = 0.1;
mat = {'Isola 370HR (FR-4)', 'Rogers AD1000'}; Dk = [3.92 10.3]; Df = [0.025 0.0023];
h = fig_new(16,7.5); hold on; box on; grid on; cl = {'r','b'};
for k = 1:2
  a = 8.686*pi*f*sqrt(Dk(k))*Df(k)/c*L;
  plot(f/1e9, a, 'Color', cl{k});
end
plot([4 4],[0 5],'k:'); text(4.1,2.6,{'4 ГГц – частота Найквиста','при 8 Гбит/с'});
xlabel('Частота, ГГц'); ylabel('Потери, дБ'); ylim([0 5]);
legend(rus(sprintf('%s: D_k = %.2f, D_f = %.3f', mat{1}, Dk(1), Df(1))), rus(sprintf('%s: D_k = %.1f, D_f = %.4f', mat{2}, Dk(2), Df(2))),'Location','northwest');
for k=1:2, fprintf('%s: 4GHz %.2f dB, 10GHz %.2f dB, delay %.2f ns\n', mat{k}, 8.686*pi*4e9*sqrt(Dk(k))*Df(k)/c*L, 8.686*pi*10e9*sqrt(Dk(k))*Df(k)/c*L, sqrt(Dk(k))*L/c*1e9); end
fig_save(h,'f15_pcb_loss');
