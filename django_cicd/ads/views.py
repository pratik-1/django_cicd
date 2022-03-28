from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse

from ads.models import Ad, Comment, Fav
from ads.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView
from ads.forms import CreateForm, CommentForm
from django.db.models import Q


# Create your views here.
# class AdListView(OwnerListView):
#     model = Ad

class AdListView(View):
    # model = Ad
    template_name = 'ads/ad_list.html'
    def get(self, request):
        strval = request.GET.get('search', False)
        if strval:
            query = Q(title__icontains=strval)
            query.add(Q(text__icontains=strval), Q.OR)
            ad_list = Ad.objects.filter(query).select_related().order_by('-updated_at')
        else:
            ad_list = Ad.objects.all().order_by('-updated_at')
        favs = list()
        if request.user.is_authenticated:
            rows = request.user.favorite_ads.values('id')
            favs = [row['id'] for row in rows]

        ctx = {'ad_list':ad_list, 'favorites': favs}
        return render(request, self.template_name, ctx)



class AdDetailView(OwnerDetailView):
    model = Ad
    template_name = "ads/ad_detail.html"

    def get(self, request, pk):
        ad = get_object_or_404(Ad, pk=pk)
        comments = Comment.objects.filter(ad=ad).order_by('-updated_at')
        comment_form = CommentForm()
        ctx = {'comment_form': comment_form, 'comments': comments, 'ad': ad}
        return render(request, self.template_name, ctx)



    # model = Forum
    # template_name = "forums/detail.html"
    # def get(self, request, pk) :
    #     x = Forum.objects.get(id=pk)
    #     comments = Comment.objects.filter(forum=x).order_by('-updated_at')
    #     comment_form = CommentForm()
    #     context = { 'forum' : x, 'comments': comments, 'comment_form': comment_form }
    #     return render(request, self.template_name, context)


class AdCreateView(LoginRequiredMixin, View):
    success_url = reverse_lazy('ads:all')
    template_name = 'ads/ad_form.html'

    def get(self, request):
        form = CreateForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request):
        form = CreateForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        ad = form.save(commit=False)
        ad.owner = self.request.user
        ad.save()
        form.save_m2m()
        return redirect(self.success_url)


class AdUpdateView(LoginRequiredMixin, View):
    success_url = reverse_lazy('ads:all')
    template_name = 'ads/ad_form.html'

    def get(self, request, pk):
        ad = get_object_or_404(Ad, id=pk, owner=self.request.user)
        form = CreateForm(instance=ad)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk):
        ad = get_object_or_404(Ad, id=pk, owner=self.request.user)
        form = CreateForm(request.POST, request.FILES or None, instance=ad)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        ad = form.save(commit=False)
        ad.owner = self.request.user
        ad.save()
        form.save_m2m()
        return redirect(self.success_url)


class AdDeleteView(OwnerDeleteView):
    model = Ad




def stream_file(request, pk):
    ad = get_object_or_404(Ad, id=pk)
    response = HttpResponse()
    response['content-type'] = ad.content_type
    response['content-lenth'] = len(ad.picture)
    response.write(ad.picture)
    return response



class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        ad = get_object_or_404(Ad, id=pk)
        comment = Comment(text=request.POST['comment'], owner=request.user,
        ad=ad)
        comment.save()
        return redirect(reverse('ads:ad_detail', args=[pk]))


class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "ads/ad_comment_delete.html"

    def get_success_url(self):
        ad = self.object.ad
        return reverse('ads:ad_detail', args=[ad.id])



from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError


@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    model = Ad
    def post(self, request, pk):
        if request.user.is_authenticated:
            ad = get_object_or_404(Ad, pk=pk)
            fav = Fav(user=request.user, ad=ad)
        try:
            fav.save()  # In case of duplicate key
        except IntegrityError as e:
            pass
        return HttpResponse()


@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    model = Ad
    def post(self, request, pk):
        ad = get_object_or_404(Ad, pk=pk)
        try:
            Fav.objects.get(user=request.user, ad=ad).delete()
        except Fav.DoesNotExist as e:
            pass
        return HttpResponse()




