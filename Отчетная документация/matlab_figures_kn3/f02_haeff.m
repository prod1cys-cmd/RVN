% Рисунок: спектр радиоимпульса ПЧ и потери рассогласования полосы (формула Хаффа [24])
sinc_ = @(x) (x==0) + (x~=0).*sin(pi*x)./(pi*x + (x==0));
fif = 60e6; f = linspace(0,140e6,6000);
tau = [0.07 0.3 1.2]*1e-6; col = {'b',[0 0.6 0],[0.8 0 0.8]};
h = fig_new(16,12);
subplot(2,1,1); hold on; box on; grid on;
patch([50 70 70 50],[-60 -60 3 3],[1 0.9 0.7],'EdgeColor','none');
for k = 1:3
  x = (f-fif)*tau(k);
  S = abs(sinc_(x)) + abs(sinc_((f+fif)*tau(k)));  % спектр прямоугольного радиоимпульса
  plot(f/1e6, 20*log10(S/max(S)+1e-12), 'Color', col{k}, 'LineWidth', 1.6-0.4*(k-1));
end
ylim([-60 3]); xlim([0 140]);
xlabel('Частота, МГц'); ylabel('|S(f)|, дБ');
legend({'полоса обработки 50–70 МГц','\tau = 0,07 мкс','\tau = 0,3 мкс','\tau = 1,2 мкс'},'Location','southoutside','Orientation','horizontal');
title('Амплитудный спектр радиоимпульса с несущей 60 МГц');
subplot(2,1,2); hold on; box on; grid on;
alpha = 1.2; Bt = linspace(0.4,4,500);
CB = Bt/(4*alpha).*(1+alpha./Bt).^2;
plot(Bt, 10*log10(CB), 'b');
Bt0 = 20e6*0.07e-6; CB0 = Bt0/(4*alpha)*(1+alpha/Bt0)^2;
plot(Bt0, 10*log10(CB0), 'ro','MarkerFaceColor','r');
text(Bt0+0.08, 10*log10(CB0)+0.25, rus(sprintf('B = 20 МГц, \\tau = 0,07 мкс: B\\tau = %.2f, потери %.2f дБ', Bt0, 10*log10(CB0))));
patch([1.2 1.4 1.4 1.2],[0 0 2 2],[0.8 1 0.8],'EdgeColor','none','FaceAlpha',0.5);
xlabel('Произведение B\tau'); ylabel('Потери C_B, дБ'); ylim([0 2]);
title('Потери из-за рассогласования полосы с длительностью импульса');
fig_save(h,'f02_haeff');
