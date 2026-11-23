% Рисунок: остаточное смещение ПЧ после грубой подстройки и точная подстройка в ПЛИС
tau = 0.07e-6; f = linspace(20e6,100e6,4000); df = [-5 0 5]*1e6;
sinc_ = @(x) (x==0) + (x~=0).*sin(pi*x)./(pi*x + (x==0));
f0 = 60e6; Bw = 30e6; Hb = 1./sqrt(1+((f.^2-f0^2)./(f*Bw)).^8);
h = fig_new(16,12);
subplot(2,1,1); hold on; box on; grid on;
patch([50 70 70 50],[-40 -40 3 3],[1 0.9 0.7],'EdgeColor','none','FaceAlpha',0.6);
plot(f/1e6, 20*log10(Hb), 'k--');
cl = {'r','b',[0 0.6 0]};
for k = 1:3
  S = abs(sinc_((f-f0-df(k))*tau));
  plot(f/1e6, 20*log10(S+1e-9), 'Color', cl{k});
end
ylim([-40 3]); xlabel('Частота, МГц'); ylabel('Уровень, дБ');
legend({'полоса обработки 50–70 МГц','фильтр ПЧ 45–75 МГц','f_{ПЧ} = 55 МГц','f_{ПЧ} = 60 МГц','f_{ПЧ} = 65 МГц'},'Location','southoutside','NumColumns',3);
title('Спектр импульса 0,07 мкс при смещении ПЧ ±5 МГц');
subplot(2,1,2); hold on; box on; grid on;
t = linspace(0,1.2e-6,600);
for k = [1 3]
  plot(t*1e6, 2*pi*df(k)*t, 'Color', cl{k});
end
plot(t*1e6, 2*pi*0.083e6*t, 'k', 'LineWidth', 1.8);
xlabel('Время от начала импульса, мкс'); ylabel('Набег фазы, рад');
legend({'без точной подстройки, \Deltaf = −5 МГц','без точной подстройки, \Deltaf = +5 МГц','после цифрового переноса, \Deltaf = 0,1/\tau = 83 кГц'},'Location','northwest');
title('Набег фазы на импульсе 1,2 мкс');
fig_save(h,'f08_tuning');
