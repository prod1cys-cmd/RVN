% Рисунок: профиль синусоидальной вибрации UR E10 и передаточная функция платы
f = logspace(log10(2),log10(300),600);
a = 0.7*ones(size(f)); i1 = f<13.2; a(i1) = 0.001*(2*pi*f(i1)).^2/9.80665; a(f>100) = NaN;
h = fig_new(16,11);
subplot(2,1,1); loglog(f, a, 'b', 'LineWidth', 1.8); grid on; box on; hold on;
plot([13.2 13.2],[0.01 2],'k:');
text(3,0.3,'±1 мм'); text(30,0.85,'±0,7 g');
xlim([2 300]); ylim([0.01 2]); ylabel('Амплитуда ускорения, g'); xlabel('Частота, Гц');
title('Испытательный профиль UR E10 (общее размещение)');
subplot(2,1,2); hold on; grid on; box on; set(gca,'XScale','log','YScale','log');
fn = [60 100 150]; Q = 10; cl = {'r','b',[0 0.6 0]}; leg = {};
for k = 1:3
  r = f/fn(k); z = 1/(2*Q);
  Tr = sqrt((1+(2*z*r).^2)./((1-r.^2).^2+(2*z*r).^2));
  plot(f, Tr, 'Color', cl{k}); leg{end+1} = sprintf('f_0 = %d Гц, Q = %d', fn(k), Q);
end
patch([2 100 100 2],[0.1 0.1 30 30],[0.9 0.9 0.9],'EdgeColor','none','FaceAlpha',0.4);
xlim([2 300]); ylim([0.1 30]); xlabel('Частота, Гц'); ylabel('Коэффициент передачи');
legend(leg,'Location','northwest'); title('Одномассовая модель: передача ускорения с опор на плату');
fig_save(h,'f13_vib');
